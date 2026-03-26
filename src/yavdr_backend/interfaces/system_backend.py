import asyncio
from asyncio.subprocess import Process
import inspect
import json
import logging
import os
import threading
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass
from enum import StrEnum
from functools import wraps
from pathlib import Path
from typing import Any, Protocol
import uuid

import dotenv
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

import ansible_runner
import sdbus
from pydantic import BaseModel, Field, SecretStr
import sdbus.exceptions
from sdbus.utils.parse import parse_properties_changed


from yavdr_backend.interfaces.systemd_dbus_interface import (
    OrgFreedesktopSystemd1ManagerInterface,
)
from yavdr_backend.interfaces.systemd_unit_interface import (
    OrgFreedesktopSystemd1UnitInterface,
)


from yavdr_backend.models.auth import Login
from yavdr_backend.tools.enum_check import check_if_enum
from yavdr_backend.tools.pam import verify_user
from yavdr_backend.models.xorg import XorgConfig

YAVDR_BACKEND_INTERFACE = "de.yavdr.SystemBackend"
SYSTEMD_DBUS_INTERFACE = "org.freedesktop.systemd1"

dotenv.load_dotenv()
ANSIBLE_DIR = os.environ.get("ANSIBLE_DIR", "/etc/ansible")
JOB_LOCK = asyncio.Lock()

ORDER_LOCK = threading.Lock()


class UpdateTypeEnum(StrEnum):
    ALL = "all"
    DEBIAN = "debian"
    SNAP = "snap"
    FLATPAK = "flatpak"


def with_stopped_systemd_units(units: list[str]):
    # This wrapper masks the vdr.service, stops the unit, executes the wrapped method
    # unmasks and starts the unit again.
    def with_stopped_systemd_service_real(function: Callable[..., None]):
        @wraps(function)
        async def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]):
            with closing(sdbus.sd_bus_open_system()) as system_bus:
                if not units:
                    return
                systemd_manager = OrgFreedesktopSystemd1ManagerInterface.new_proxy(
                    SYSTEMD_DBUS_INTERFACE, "/org/freedesktop/systemd1", bus=system_bus
                )
                unit_paths = [await systemd_manager.load_unit(unit) for unit in units]
                unit_proxies = [
                    OrgFreedesktopSystemd1UnitInterface.new_proxy(
                        SYSTEMD_DBUS_INTERFACE, unit_path, bus=system_bus
                    )
                    for unit_path in unit_paths
                ]

                async def wait_for_unit_change(active_state: str, sub_state: str):
                    async for s in unit_proxy.properties_changed:
                        p = parse_properties_changed(
                            OrgFreedesktopSystemd1UnitInterface, s, "ignore"
                        )
                        print(p)
                        if (
                            p.get("active_state") == active_state
                            and p.get("sub_state") == sub_state
                        ):
                            return

                try:
                    await systemd_manager.mask_unit_files(units, True, True)
                    async with asyncio.TaskGroup() as group:
                        for unit_proxy in unit_proxies:
                            group.create_task(wait_for_unit_change("inactive", "dead"))
                            group.create_task(unit_proxy.stop("replace"))
                    if inspect.iscoroutinefunction(function):
                        return await function(*args, **kwargs)
                    else:
                        return function(*args, **kwargs)
                finally:
                    print(f"unmasking and starting {units}")
                    await systemd_manager.unmask_unit_files(units, True)
                    async with asyncio.TaskGroup() as group:
                        for unit_proxy in unit_proxies:
                            group.create_task(wait_for_unit_change("active", "running"))
                            group.create_task(unit_proxy.start("replace"))

        return wrapper

    return with_stopped_systemd_service_real


class Playbooks(StrEnum):
    RESCAN_DISPLAYS = "rescan-displays.yml"
    APPLY_DISPLAY_CONFIG = "apply-display-config.yml"
    INSTALL_FULL = "yavdr07.yml"


class Status(StrEnum):
    DONE = "done"
    NEW = "new"
    STARTING = "starting"


# actions = {
#     Playbooks.RESCAN_DISPLAYS: rescan_displays
# }

# class StatusData(BaseModel):
#     status: str
#     runner_ident: str


class Job(Protocol):
    uuid: str

    async def run(self) -> None: ...


@dataclass
class UpdateJob(Job):
    uuid: str
    update_type: UpdateTypeEnum
    backend: "YavdrSystemBackend"

    async def run(self) -> None:
        print(f"running update job, {self.uuid=}, {self.update_type=}")

        async def emit_output(p: Process, self: "UpdateJob"):
            print(f"called emit_output for {p=}")
            if p.stdout:
                print(f"watching output of {p}")
                async for line in p.stdout:
                    if line:
                        print(line)
                        # Decode mit 'replace' um Fehler bei Sonderzeichen in Fortschrittsbalken zu vermeiden
                        output = line.decode(errors="replace").rstrip()
                        self.backend.process_event.emit(
                            (self.uuid, "output", f'{{"msg": "{output}"}}')
                        )
                s, e = await p.communicate()
                print(f"{s=}, {e=}")

        async def system_update():
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            env["DEBIAN_FRONTEND"] = "noninteractive"
            p = await asyncio.create_subprocess_exec(
                "apt",
                "update",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
            )
            await emit_output(p, self)

            if p.returncode != 0:
                raise ValueError("apt update failed")
            # u = await asyncio.create_subprocess_exec(
            u = await asyncio.create_subprocess_shell(
                'apt-get full-upgrade -y -o Dpkg::Options::="--force-confold" -o Dpkg::Options::="--force-confdef"',
                # "apt-get",
                # "dist-upgrade",
                # "-y",
                # "-o",
                # 'Dpkg::Options::="--force-confdef"',
                # "-o",
                # 'Dpkg::Options::="--force-confold"',
                env={"DEBIAN_FRONTEND": "noninteractive"},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            await emit_output(u, self)

            if u.returncode != 0:
                raise ValueError("apt-get full-upgrade failed")

        async def snap_update():
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            p = await asyncio.create_subprocess_exec(
                "snap",
                "refresh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
            )
            print(f"created snap update job: {p=}")
            await emit_output(p, self)
            print(f"done listening to {p=}")
            if p.returncode != 0:
                raise ValueError("snap update failed")

        async def flatpak_update():
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            p = await asyncio.create_subprocess_exec(
                "flatpak",
                "update",
                "--noninteractive",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
            )
            print(f"created flatpak_update job: {p=}")
            await emit_output(p, self)
            print(f"done listening to {p=}")
            if p.returncode != 0:
                raise ValueError("flatpak update failed")

            p = await asyncio.create_subprocess_exec(
                "flatpak",
                "uninstall",
                "--unused",
                "--noninteractive",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
            )
            await emit_output(p, self)
            if p.returncode != 0:
                raise ValueError("flatpak uninstall failed")

            p = await asyncio.create_subprocess_shell(
                r"""\
                test -f /proc/driver/nvidia/version || exit 0;
                installed_version=$(grep -m1 -Po '\d+\.\d+' /proc/driver/nvidia/version);
                version_part=$(sed 's/\./-/g' <<< "$installed_version");
                grep -q "^nvidia-${version_part}" < <(flatpak list) && exit 0 || exit 1""",
                executable="/usr/bin/bash",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=env,
            )
            await emit_output(p, self)
            if p.returncode != 0:
                raise ValueError("removing old nvidia drivers failed")

        try:
            print("Run update for {self.update_type}")
            self.backend.process_event.emit(
                (
                    self.uuid,
                    str(Status.STARTING),
                    f"{{'msg': 'Run update for {self.update_type}'}}",
                )
            )
            match self.update_type:
                case UpdateTypeEnum.ALL:
                    await system_update()
                    await snap_update()
                    await flatpak_update()
                case UpdateTypeEnum.DEBIAN:
                    await system_update()
                case UpdateTypeEnum.SNAP:
                    await snap_update()
                case UpdateTypeEnum.FLATPAK:
                    await flatpak_update()
        # except Exception as err:
        #     return False, str(err)

        # else:
        #     return True, "success"
        finally:
            self.backend.process_event.emit(
                (
                    self.uuid,
                    str(Status.DONE),
                    f'{{"msg": "Ended update for {self.update_type}", "status": "done"}}',
                )
            )


@dataclass
class SubprocessJob(Job):
    uuid: str
    command: list[str] | str
    backend: "YavdrSystemBackend"
    env: dict[str, str]

    async def run(self) -> None:
        if not self.command:
            raise ValueError("Empty command")
        if isinstance(self.command, str):
            p = await asyncio.create_subprocess_shell(
                self.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env=self.env,
            )
        else:
            p = await asyncio.create_subprocess_exec(
                *self.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,  # stderr in stdout mergen für einfacheres Logging
                env=self.env,
            )
        if p.stdout:
            while line := await p.stdout.readline():
                self.backend.process_event.emit(
                    ("STDOUT", self.uuid, line.decode(errors="replace"))
                )


@dataclass
class FileJob(Job):
    # model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: str
    file_content: bytes
    filepath: Path
    required_stopped_services: list[str]
    backend: "YavdrSystemBackend"

    async def run(self) -> None:
        systemd_manager = OrgFreedesktopSystemd1ManagerInterface.new_proxy(
            SYSTEMD_DBUS_INTERFACE,
            "/org/freedesktop/systemd1",
            bus=self.backend.system_bus,
        )
        units_to_start_again: list[OrgFreedesktopSystemd1UnitInterface] = []
        async with asyncio.timeout(delay=60):
            async with asyncio.TaskGroup() as group:

                async def wait_for_unit_stop(
                    unit_proxy: OrgFreedesktopSystemd1UnitInterface,
                ):
                    async for s in unit_proxy.properties_changed:
                        print(
                            f"got status change for {unit_proxy.names}:",
                            p := parse_properties_changed(
                                OrgFreedesktopSystemd1UnitInterface, s, "ignore"
                            ),
                        )
                        if p.get("active_state") in ("failed", "inactive") and p.get(
                            "sub_state"
                        ) in ("stopped", "dead", "failed"):
                            print(f"unit {unit_proxy.names} stopped")
                            return

                for unit in self.required_stopped_services:
                    print(f"stopping {unit=}")
                    object_path = await systemd_manager.load_unit(unit)
                    await systemd_manager.mask_unit_files(
                        self.required_stopped_services, True, True
                    )
                    print(f"load unit: {object_path=}")
                    unit_proxy = OrgFreedesktopSystemd1UnitInterface.new_proxy(
                        service_name="org.freedesktop.systemd1",
                        object_path=object_path,
                        bus=self.backend.system_bus,
                    )
                    print("checking state of unit...")
                    active_state = await unit_proxy.active_state.get_async()
                    print(f"state of unit was: {active_state=}")
                    if active_state in ("active", "reloading", "activating"):
                        print("unit seems to be active, adding to list to restart...")
                        units_to_start_again.append(unit_proxy)

                    group.create_task(wait_for_unit_stop(unit_proxy))
                    group.create_task(unit_proxy.stop("replace"))

        print(f"writing file {self.filepath}...")

        self.filepath.write_bytes(self.file_content)
        print(f"written file {self.filepath}")

        await systemd_manager.unmask_unit_files(self.required_stopped_services, True)
        print(f"unmasked unit files {self.required_stopped_services}")
        async with asyncio.TaskGroup() as group:
            for unit_proxy in units_to_start_again:
                print(f"creating task to start {await unit_proxy.source_path} again...")
                group.create_task(unit_proxy.start("replace"))
        print("FileJob done")
        self.backend.file_event.emit((Status.DONE, "file saved"))

        return


@dataclass
class AnsibleJob:
    uuid: str
    playbook: str
    backend: "YavdrSystemBackend"
    extravars: dict[str, Any] = Field(default_factory=dict)
    current_runner: str = ""

    def _status_handler(self, status_data: dict[str, str], runner_config: Any) -> None:
        print(f"{status_data=}")
        # print(f"{runner_config=}")
        if not self.current_runner and status_data.get("status") == Status.STARTING:
            self.current_runner = status_data.get("runner_ident", "")
            print((str(Status.STARTING), f"{self.uuid} {self.current_runner}"))
            # TODO if the runner uses the given uuid, we don't need those Status events
            self.backend.ansible_event.emit(
                (self.uuid, str(Status.STARTING), f"{self.uuid} {self.current_runner}")
            )
        self.backend.ansible_event.emit(
            (
                self.uuid,
                status_data.get("runner_ident", ""),
                json.dumps({"status": status_data}, skipkeys=True),
            )
        )
        if status_data.get("status") in ("successful", "failed", "timeout"):
            self.backend.ansible_event.emit(
                (self.uuid, Status.DONE, self.current_runner)
            )
            self.current_runner = ""

    def _event_handler(self, event_data: dict[str, Any]) -> None:
        print(f"{event_data=}")
        self.backend.ansible_event.emit(
            (
                self.uuid,
                event_data.get("runner_ident", ""),
                json.dumps({"event": event_data}, skipkeys=True),
            )
        )

    async def run(self) -> None:
        logging.info(
            f"adding AnsibleJob with {self.uuid=}: {self.playbook=} - {self.extravars=}"
        )
        try:
            _thread = await asyncio.to_thread(
                ansible_runner.run,  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                private_data_dir=ANSIBLE_DIR,
                playbook=self.playbook,
                ident=self.uuid,
                status_handler=self._status_handler,
                event_handler=self._event_handler,
                # finished_callback=self._finished_callback,
                extravars=self.extravars,
            )
        except Exception:
            logging.exception("running playbook failed")
        print(f"job {self.uuid} finished")
        # self.ansible_event.emit(self.uuid, Status.DONE)


class FileOption(BaseModel):
    filepath: Path
    required_stopped_services: list[str] = Field(default_factory=list)


class AllowedSystemConfigfiles(StrEnum):
    AVAHI_LINKER = "/etc/avahi-linker/default.cfg"
    YAVDR_FRONTEND = "/etc/yavdr-frontend/config.yml"
    ACPIWAKEUP = "/etc/vdr/vdr-addon-acpiwakeup.conf"
    PICOIRMP_WAKEUP = "/etc/vdr/vdr-addon-picoirmp-wakeup.conf"
    STM32_WAKEUP = "/etc/vdr/vdr-addon-stm32irmp-wakeup.conf"
    LIFEGUARD = "/etc/lifeguard.conf"
    LIFEGUARD_NG = "/etc/lifeguard.yml"
    RC_MAPS = "/etc/rc_maps.cfg"


allowed_system_config_files_options: dict[AllowedSystemConfigfiles, FileOption] = {
    AllowedSystemConfigfiles.AVAHI_LINKER: FileOption(
        filepath=Path(AllowedSystemConfigfiles.AVAHI_LINKER),
        required_stopped_services=["avahi-linker.service"],
    ),
    AllowedSystemConfigfiles.YAVDR_FRONTEND: FileOption(
        filepath=Path(AllowedSystemConfigfiles.YAVDR_FRONTEND),
        required_stopped_services=["yavdr-xorg"],
    ),
    AllowedSystemConfigfiles.LIFEGUARD: FileOption(
        filepath=Path(AllowedSystemConfigfiles.LIFEGUARD),
        required_stopped_services=[],
    ),
    AllowedSystemConfigfiles.LIFEGUARD_NG: FileOption(
        filepath=Path(AllowedSystemConfigfiles.LIFEGUARD_NG),
        required_stopped_services=[],
    ),
    AllowedSystemConfigfiles.ACPIWAKEUP: FileOption(
        filepath=Path(AllowedSystemConfigfiles.ACPIWAKEUP),
        required_stopped_services=[],
    ),
    AllowedSystemConfigfiles.PICOIRMP_WAKEUP: FileOption(
        filepath=Path(AllowedSystemConfigfiles.PICOIRMP_WAKEUP),
        required_stopped_services=[],
    ),
    AllowedSystemConfigfiles.STM32_WAKEUP: FileOption(
        filepath=Path(AllowedSystemConfigfiles.STM32_WAKEUP),
        required_stopped_services=[],
    ),
    AllowedSystemConfigfiles.RC_MAPS: FileOption(
        filepath=Path(AllowedSystemConfigfiles.RC_MAPS),
        required_stopped_services=[],
    ),
}


class AllowedVDRConfigfiles(StrEnum):
    # IMPORTANT: this is the whitelist for all config files
    CHANNELS = "channels.conf"
    REMOTE = "remote.conf"
    KEYMACROS = "keymacros.conf"
    DISQC = "diseqc.conf"
    SOURCES = "sources.conf"
    SETUP = "setup.conf"
    MENUORG = "menuorg.xml"


VDR_CONFIG_DIR = Path("/var/lib/vdr")

allowed_vdr_config_files_options: dict[AllowedVDRConfigfiles, FileOption] = {
    AllowedVDRConfigfiles.CHANNELS: FileOption(
        filepath=VDR_CONFIG_DIR / "channels.conf",
        required_stopped_services=["vdr.service"],
    ),
    AllowedVDRConfigfiles.REMOTE: FileOption(
        filepath=VDR_CONFIG_DIR / "remote.conf",
        required_stopped_services=["vdr.service"],
    ),
    AllowedVDRConfigfiles.KEYMACROS: FileOption(
        filepath=VDR_CONFIG_DIR / "keymacros.conf",
        required_stopped_services=["vdr.service"],
    ),
    AllowedVDRConfigfiles.DISQC: FileOption(
        filepath=VDR_CONFIG_DIR / "diseqc.conf",
        required_stopped_services=["vdr.service"],
    ),
    AllowedVDRConfigfiles.SOURCES: FileOption(
        filepath=VDR_CONFIG_DIR / "sources.conf",
        required_stopped_services=["vdr.service"],
    ),
    AllowedVDRConfigfiles.SETUP: FileOption(
        filepath=VDR_CONFIG_DIR / "setup.conf",
        required_stopped_services=["vdr.service"],
    ),
    AllowedVDRConfigfiles.MENUORG: FileOption(
        filepath=VDR_CONFIG_DIR / "plugins/menuorg.xml", required_stopped_services=[]
    ),
}


def get_backend(system_bus: sdbus.SdBus):
    return YavdrSystemBackend(system_bus).new_proxy(
        YAVDR_BACKEND_INTERFACE, "/", system_bus
    )


class YavdrSystemBackend(
    sdbus.DbusInterfaceCommonAsync, interface_name=YAVDR_BACKEND_INTERFACE
):
    job_queue: asyncio.Queue[Job] = asyncio.Queue()
    job_uuid: str = ""
    current_runner: str = ""

    def __init__(self, systembus: sdbus.SdBus):
        self.system_bus = systembus
        super().__init__()

    async def run_jobs(self):
        while True:
            job = await self.job_queue.get()
            self.current_job_uuid = job.uuid
            async with JOB_LOCK:
                await job.run()
                self.job_uuid = ""
                self.job_queue.task_done()

    @sdbus.dbus_method_async(
        input_signature="ss", result_signature="b", flags=sdbus.DbusUnprivilegedFlag
    )
    async def check_login(self, username: str, password: str) -> bool:
        try:
            login = Login(username=username, password=SecretStr(password))
            return verify_user(login.username, login.password.get_secret_value())
        except Exception as err:
            logging.warning(err)
            return False

    @sdbus.dbus_property_async("s")
    def get_current_job(self):
        return self.job_uuid

    @sdbus.dbus_property_async("s")
    def get_current_runner(self):
        return self.current_runner

    @sdbus.dbus_method_async(
        input_signature="s", result_signature="s", flags=sdbus.DbusUnprivilegedFlag
    )
    async def install_yavdr_full(self, playbook_variables: str) -> str:
        config: dict[str, Any] = (
            json.loads(playbook_variables) if playbook_variables else {}
        )
        job_uuid = str(uuid.uuid1())
        self.job_uuid = f"{job_uuid}"
        self.job_queue.put_nowait(
            AnsibleJob(
                uuid=job_uuid,
                playbook=Playbooks.INSTALL_FULL,
                extravars=config,
                backend=self,
                current_runner="",
            )
        )
        return str(job_uuid)

    @sdbus.dbus_method_async(
        input_signature="", result_signature="s", flags=sdbus.DbusUnprivilegedFlag
    )
    async def rescan_displays(self) -> str:
        print("rescan displays ...")
        logging.info("called rescan_display()")
        job_uuid = str(uuid.uuid1())
        self.job_uuid = f"{job_uuid}"
        self.job_queue.put_nowait(
            AnsibleJob(
                uuid=job_uuid,
                playbook=Playbooks.RESCAN_DISPLAYS,
                extravars=dict(),
                backend=self,
                current_runner="",
            )
        )
        return str(job_uuid)

    @sdbus.dbus_method_async(input_signature="s", flags=sdbus.DbusUnprivilegedFlag)
    async def write_display_configuration(self, config: str) -> None:
        logging.debug(f"called {__name__} with {config=}")
        try:
            validated_config = XorgConfig(**json.loads(config))
            yaml = YAML()
            yaml.default_flow_style = False
            yaml.indent(mapping=2, sequence=4, offset=2)  # pyright: ignore[reportUnknownMemberType]
            content = CommentedMap(validated_config.model_dump(mode="json"))
            content.yaml_set_start_comment(
                "run 'sudo yavdr-config run-display-config' to apply changes of this file to the system"
            )  # pyright: ignore[reportUnknownMemberType]
            with open(Path("/etc/yavdr/display_config.yml"), "w") as f:
                yaml.dump(data=content, stream=f)  # pyright: ignore[reportUnknownMemberType]

        except Exception:
            logging.exception("failed to save diplay config")
            raise

    @sdbus.dbus_method_async(
        input_signature="", result_signature="s", flags=sdbus.DbusUnprivilegedFlag
    )
    async def set_display_configuration(self) -> str:
        print("configure display settings ...")
        job_uuid = str(uuid.uuid1())
        self.job_uuid = f"{job_uuid}"
        self.job_queue.put_nowait(
            AnsibleJob(
                uuid=job_uuid,
                playbook=Playbooks.APPLY_DISPLAY_CONFIG,
                extravars={},
                backend=self,
                current_runner="",
            )
        )
        return str(job_uuid)

    @sdbus.dbus_signal_async(signal_signature="sss")
    def process_event(self) -> tuple[str, str, str]:
        raise NotImplementedError

    @sdbus.dbus_signal_async(signal_signature="sss")
    def ansible_event(self) -> tuple[str, str, str]:
        raise NotImplementedError

    @sdbus.dbus_signal_async(signal_signature="ss")
    def file_event(self) -> tuple[str, str]:
        raise NotImplementedError

    @sdbus.dbus_method_async(
        input_signature="sh", result_signature="s", flags=sdbus.DbusUnprivilegedFlag
    )
    async def save_file(self, name: str, fd: int) -> str:
        # TODO: we need to run longer actions in the background and send a signal once we are done
        # the return value is the job_id for the job, if there is no job necessary, an empty string is returned
        print(f"called save_file with {name=}, {fd=}")
        try:
            if check_if_enum(name, AllowedVDRConfigfiles):
                name = AllowedVDRConfigfiles(name)
                options = allowed_vdr_config_files_options[name]
                print("got VDR Config file")
            elif check_if_enum(name, AllowedSystemConfigfiles):
                name = AllowedSystemConfigfiles(name)
                options = allowed_system_config_files_options[name]
                print("got System Config file")
            else:
                raise ValueError(f"unknown config file {name}")
            with open(fd, "rb", closefd=False) as input_file:
                input_file.seek(0)
                content = input_file.read()
        except Exception as err:
            print(err)
            logging.error(
                f"method {__name__}: got non-whitelisted {name=}: {err}"
                if isinstance(err, ValueError)
                else f"method {__name__}: no configuration for {name=}: {err}"
            )
            raise sdbus.exceptions.DbusInvalidArgsError(
                f"method {__name__}: got non-whitelisted {name=}"
                if isinstance(err, ValueError)
                else f"method {__name__}: no configuration for {name=}"
            )
        else:
            job_uuid = str(uuid.uuid1())
            if len(options.required_stopped_services) == 0:
                # if we only need to write the file, we can return early
                print(f"writing data from {fd=} to {options.filepath=}...")
                # important: the filedescriptor if the input file is managed by the caller!
                options.filepath.write_bytes(content)
                self.file_event.emit((Status.DONE, str(job_uuid)))
                print(f"written file for {job_uuid}")
            else:
                print(f"queing job {job_uuid} ...")
                # otherwise we need to create a job and run it in the background
                try:
                    self.job_queue.put_nowait(
                        FileJob(
                            uuid=job_uuid,
                            file_content=content,
                            filepath=options.filepath,
                            required_stopped_services=options.required_stopped_services,
                            backend=self,
                        )
                    )
                except Exception as err:
                    print("Error when queuing FileJob:", err)

            return job_uuid

    @sdbus.dbus_method_async(
        input_signature="s", result_signature="s", flags=sdbus.DbusUnprivilegedFlag
    )
    async def update(self, update_type: UpdateTypeEnum) -> str:
        print(f"called update with {update_type=}")
        # TODO: put into background job, forward events as dbus signals
        job_uuid = str(uuid.uuid1())

        try:
            self.job_queue.put_nowait(
                UpdateJob(uuid=job_uuid, update_type=update_type, backend=self)
            )
        except Exception as err:
            print("could not queue job:", err)
            raise

        return job_uuid

    @sdbus.dbus_method_async(flags=sdbus.DbusUnprivilegedFlag)
    async def reboot(
        self,
    ):
        p = await asyncio.create_subprocess_exec("systemctl", "reboot", "-i")

    @sdbus.dbus_method_async(flags=sdbus.DbusUnprivilegedFlag)
    async def poweroff(
        self,
    ):
        p = await asyncio.create_subprocess_exec("systemctl", "poweroff", "-i")


# async def main():
#     system_bus = sdbus.sd_bus_open_system()
#     backend_interface = YavdrSystemBackend(system_bus)
#     await system_bus.request_name_async(YAVDR_BACKEND_INTERFACE, 0)
#     backend_interface.export_to_dbus("/", system_bus)
#     await backend_interface.run_jobs()
#     # await asyncio.Future()


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         pass
