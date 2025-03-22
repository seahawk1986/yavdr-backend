import asyncio
from dataclasses import dataclass
from functools import wraps
import inspect
import json
import logging
from pathlib import Path
import threading
from enum import StrEnum
from typing import Any, Callable, Protocol
from uuid import UUID
import uuid

import ansible_runner
import sdbus
from pydantic import BaseModel, Field, ConfigDict
import sdbus.exceptions
from sdbus.utils.parse import parse_properties_changed


# from app.interfaces.systemd_dbus_interface import OrgFreedesktopSystemd1ManagerInterface
# from app.interfaces.systemd_unit_interface import OrgFreedesktopSystemd1UnitInterface


from app.interfaces.systemd_dbus_interface import OrgFreedesktopSystemd1ManagerInterface
from app.interfaces.systemd_unit_interface import OrgFreedesktopSystemd1UnitInterface


YAVDR_BACKEND_INTERFACE = "de.yavdr.SystemBackend"
SYSTEMD_DBUS_INTERFACE = "org.freedesktop.systemd1"

ANSIBLE_DIR = "/home/demo/yavdr-ansible"
JOB_LOCK = threading.Lock()

ORDER_LOCK = threading.Lock()


def with_stopped_systemd_units(units: list[str]):
    # This wrapper masks the vdr.service, stops the unit, executes the wrapped method
    # unmasks and starts the unit again.
    def with_stopped_systemd_service_real(function: Callable):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            system_bus = sdbus.sd_bus_open_system()
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
    uuid: UUID

    async def run(self) -> Any: ...


@dataclass
class FileJob():
    # model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: UUID
    file_content: bytes
    filepath: Path
    required_stopped_services: list[str]
    backend: "YavdrSystemBackend"

    async def run(self):
        systemd_manager = OrgFreedesktopSystemd1ManagerInterface.new_proxy(
            SYSTEMD_DBUS_INTERFACE,
            "/org/freedesktop/systemd1",
            bus=self.backend.system_bus,
        )
        units_to_start_again: list[OrgFreedesktopSystemd1UnitInterface] = []
        async with asyncio.TaskGroup() as group:

            async def wait_for_unit_stop(
                unit_proxy: OrgFreedesktopSystemd1UnitInterface,
            ):
                async for s in unit_proxy.properties_changed:
                    print(f"got status change for {unit_proxy.names}:",
                        p := parse_properties_changed(
                            OrgFreedesktopSystemd1UnitInterface, s, "ignore"
                        )
                    )
                    if p.get("active_state") in ("failed", "inactive") and p.get(
                        "sub_state"
                    ) in ("stopped", "dead"):
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


class AnsibleJob(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    uuid: UUID
    playbook: str
    extravars: dict[str, Any] = Field(default_factory=dict)
    current_runner: str = ""
    backend: "YavdrSystemBackend"

    def _status_handler(self, status_data: dict[str, str], runner_config):
        print(f"{status_data=}")
        # print(f"{runner_config=}")
        if not self.current_runner and status_data.get("status") == Status.STARTING:
            self.current_runner = status_data.get("runner_ident", "")
            print((str(Status.STARTING), f"{self.uuid} {self.current_runner}"))
            self.backend.ansible_event.emit(
                (str(Status.STARTING), f"{self.uuid} {self.current_runner}")
            )
        self.backend.ansible_event.emit(
            (
                status_data.get("runner_ident", ""),
                json.dumps({"status": status_data}, skipkeys=True),
            )
        )
        if status_data.get("status") in ("successful", "failed", "timeout"):
            self.backend.ansible_event.emit((Status.DONE, self.current_runner))
            self.current_runner = ""

    def _event_handler(self, event_data):
        print(f"{event_data=}")
        self.backend.ansible_event.emit(
            (
                event_data.get("runner_ident", ""),
                json.dumps({"event": event_data}, skipkeys=True),
            )
        )

    async def run(self):
        await asyncio.to_thread(
            ansible_runner.run,
            private_data_dir=ANSIBLE_DIR,
            playbook=self.playbook,
            status_handler=self._status_handler,
            event_handler=self._event_handler,
            # finished_callback=self._finished_callback,
            extravars=self.extravars,
        )
        print(f"job {self.uuid} finished")
        # self.ansible_event.emit(Status.DONE)


class AllowedVDRConfigfiles(StrEnum):
    # IMPORTANT: this is the whitelist for all config files
    CHANNELS = "channels.conf"
    REMOTE = "remote.conf"
    KEYMACROS = "keymacros.conf"
    DISQC = "diseqc.conf"
    SOURCES = "sources.conf"
    SETUP = "setup.conf"
    MENUORG = "menuorg.xml"


class FileOption(BaseModel):
    filepath: Path
    required_stopped_services: list[str] = Field(default_factory=list)


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


class YavdrSystemBackend(
    sdbus.DbusInterfaceCommonAsync, interface_name=YAVDR_BACKEND_INTERFACE
):
    job_queue: asyncio.Queue[Job] = asyncio.Queue()
    job_uuid: str = ""
    current_runner: str = ""

    def __init__(self, systembus):
        self.system_bus = systembus
        super().__init__()

    async def run_jobs(self):
        while True:
            job = await self.job_queue.get()
            self.current_job_uuid = job.uuid
            # self.ansible_event.emit(f"{Status.NEW} {job.uuid}")
            with JOB_LOCK:
                await job.run()
                self.job_uuid = ""
                self.job_queue.task_done()

    @sdbus.dbus_property_async("s")
    def get_current_job(self):
        return self.job_uuid

    @sdbus.dbus_property_async("s")
    def get_current_runner(self):
        return self.current_runner

    @sdbus.dbus_method_async(
        input_signature="", result_signature="s", flags=sdbus.DbusUnprivilegedFlag
    )
    async def rescan_displays(self) -> str:
        print("rescan displays ...")
        job_uuid = uuid.uuid1()
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

    @sdbus.dbus_signal_async(signal_signature="ss")
    def ansible_event(self):
        raise NotImplementedError

    @sdbus.dbus_signal_async(signal_signature="ss")
    def file_event(self):
        raise NotImplementedError

    @sdbus.dbus_method_async(
        input_signature="sh", result_signature="s", flags=sdbus.DbusUnprivilegedFlag
    )
    async def save_file(self, name: str, fd: int) -> str:
        # TODO: we need to run longer actions in the background and send a signal once we are done
        # the return value is the job_id for the job, if there is no job necessary, an empty string is returned
        print(f"called save_file with {name=}, {fd=}")
        try:
            name = AllowedVDRConfigfiles(name)
            options = allowed_vdr_config_files_options[name]
            with open(fd, "rb", closefd=False) as input_file:
                input_file.seek(0)
                content = input_file.read()
        # except (ValueError, KeyError) as err:
        except Exception as err:
            print(err)
            logging.error(
                f"method {__name__}: got non-whitelisted {name=}"
                if isinstance(err, ValueError)
                else f"method {__name__}: no configuration for {name=}"
            )
            raise sdbus.exceptions.DbusInvalidArgsError(
                f"method {__name__}: got non-whitelisted {name=}"
                if isinstance(err, ValueError)
                else f"method {__name__}: no configuration for {name=}"
            )
        else:
            job_uuid = uuid.uuid1()
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

            return str(job_uuid)

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
