# Module for system information (and possible operations)
import asyncio
from contextlib import closing
import contextlib
import json
import logging
from pathlib import Path
import sys
import tempfile
from typing import Annotated, Any
from fastapi.responses import FileResponse
import sdbus
from threading import Lock
from collections.abc import Mapping

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import BaseModel
from ruamel.yaml import YAML
from sse_starlette import EventSourceResponse

from yavdr_backend.interfaces.system_backend import (
    AllowedSystemConfigfiles,
    allowed_system_config_files_options,
    YavdrSystemBackend,
    Status,
    YAVDR_BACKEND_INTERFACE,
    UpdateTypeEnum,
)
from yavdr_backend.models.xorg import XorgConfig
from yavdr_backend.routers.auth import User, get_current_active_user
# from interfaces.system_backend import YAVDR_BACKEND_INTERFACE


router = APIRouter()
ANSIBLE_LOCK = Lock()


class Playbook(BaseModel):
    playbook: str
    options: Mapping[str, Any]


@router.post("/system/playbook/rescan_displays")
async def run_playbook(
    request: Request, current_user: User = Depends(get_current_active_user)
):
    """forward dbus2vdr's signals as Server Side Events"""

    async def event_generator():
        with closing(sdbus.sd_bus_open_system()) as system_bus:
            backend_connection = YavdrSystemBackend(system_bus).new_proxy(
                YAVDR_BACKEND_INTERFACE, "/", system_bus
            )
            try:
                job_uuid = await backend_connection.rescan_displays()
            except Exception:
                logging.exception("failure when awaiting run rescan_displays()")
                return
            async for event in backend_connection.ansible_event:
                # yield event
                current_job_uuid, message_type, message = event
                if current_job_uuid != job_uuid:
                    continue
                if message_type == Status.STARTING:
                    print("start of stream")
                    continue
                if message_type == Status.DONE:
                    print("end of stream ...")
                    return
                if await request.is_disconnected():
                    break
                else:
                    yield message

    return EventSourceResponse(event_generator(), send_timeout=5)


@router.get("/system/display_config")
async def get_xorg_config(
    current_user: User = Depends(get_current_active_user),
) -> XorgConfig:
    config_file = Path("/etc/yavdr/display_config.yml")
    yaml = YAML(typ="safe")
    try:
        with open(config_file) as f:
            data: dict[str, Any] = yaml.load(f)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    except IOError:
        fallback_config_file = Path("/etc/ansible/facts.d/display_config.fact")
        print(f"fallback to {fallback_config_file=}")
        try:
            with open(fallback_config_file) as f:
                data = json.load(f)
                print(f"got json data: {data}")
        except Exception:
            logging.exception("could not load monitor_config, please rescan displays")
            raise ValueError(
                'could not load "/etc/ansible/facts.d/display_config.fact", please rescan displays'
            )

    print(f"{data=}")
    config: XorgConfig = XorgConfig.model_validate(data)
    return config


@router.get("/system/display_outputs")
async def get_xrandr_facts(
    current_user: User = Depends(get_current_active_user),
) -> FileResponse:
    return FileResponse(
        "/etc/ansible/facts.d/display_outputs.fact",
        headers={"Cache-Control": "no-store"},
    )


# @router.get("/system/display_config")
# async def get_xorg_config_facts(
#     current_user: User = Depends(get_current_active_user),
# ) -> FileResponse:
#     return FileResponse(
#         "/etc/ansible/facts.d/display_config.fact",
#         headers={"Cache-Control": "no-store"},
#     )


@router.post("/system/xorg_config")
async def set_xorg_confg(
    config: XorgConfig,
    request: Request,
    current_user: User = Depends(get_current_active_user),
) -> EventSourceResponse:
    print("post xorg_config:", config)

    async def event_generator():
        with closing(sdbus.sd_bus_open_system()) as system_bus:
            backend_connection = YavdrSystemBackend(system_bus).new_proxy(
                YAVDR_BACKEND_INTERFACE, "/", system_bus
            )
            await backend_connection.write_display_configuration(
                config.model_dump_json()
            )
            job_uuid = await backend_connection.set_display_configuration()
            runner_ident = None
            async for event in backend_connection.ansible_event:
                # yield event
                current_job_uuid, message_type, message = event
                # print(f"{message_type} - {message}")
                if await request.is_disconnected():
                    break
                if current_job_uuid != job_uuid:
                    continue
                if message_type == Status.DONE:
                    job_uuid = None
                    runner_ident = None
                    # yield message
                    # yield {'event': ,'state': 'done'}
                    print("end of stream ...")
                    return
                elif message_type == Status.STARTING:
                    _job_uuid, _runner_ident = message.split()
                    if _job_uuid == job_uuid:
                        runner_ident = _runner_ident
                        print(f"set {runner_ident=}")
                    continue
                else:
                    try:
                        data = json.loads(message)
                        if data.get("event", {}).get(
                            "runner_ident"
                        ) == runner_ident or data.get("status", {}).get("runner_ident"):
                            yield message
                    except json.JSONDecodeError as e:
                        print(e, file=sys.stderr)
                        # yield f"{e}: {message}"

    return EventSourceResponse(event_generator(), send_timeout=5)


@router.post("/system/update/{update_type}")
async def update_packages(
    update_type: UpdateTypeEnum, current_user: User = Depends(get_current_active_user)
) -> tuple[bool, str]:
    with closing(sdbus.sd_bus_open_system()) as system_bus:
        backend_connection = YavdrSystemBackend(system_bus).new_proxy(
            YAVDR_BACKEND_INTERFACE, "/", system_bus
        )
        success, message = await backend_connection.update(update_type)
        return success, message


class ConfigfileUploadData(BaseModel):
    filename: AllowedSystemConfigfiles
    uploaded_file: UploadFile


@router.get("/system/configfile")
async def get_configfile(
    filename: AllowedSystemConfigfiles,
    current_user: User = Depends(get_current_active_user),
) -> FileResponse:
    path = allowed_system_config_files_options[filename].filepath
    print(f"got request for {filename=}")
    return FileResponse(path)


@router.post("/system/configfile")
async def upload_configfile(
    filename: Annotated[AllowedSystemConfigfiles, Form()],
    uploaded_file: Annotated[UploadFile, File()],
    current_user: User = Depends(get_current_active_user),
):
    print(
        f"got {filename=} with {uploaded_file.size=} and {uploaded_file.content_type=}, {uploaded_file.headers}"
    )

    content = await uploaded_file.read()

    async def event_generator():
        with contextlib.closing(sdbus.sd_bus_open_system()) as system_bus:
            backend = YavdrSystemBackend.new_proxy(
                YAVDR_BACKEND_INTERFACE, "/", system_bus
            )

            queue: asyncio.Queue[tuple[Status, str]] = asyncio.Queue()

            async def wait_for_done():
                async for event in backend.file_event:
                    print(event)
                    event_type, _msg = event
                    await queue.put((Status(event_type), _msg))
                    if event_type == Status.DONE:
                        print("wait_for_done ends")
                        return

            async def share_file(content: bytes):
                with tempfile.TemporaryFile() as shared_file:
                    shared_file.write(content)
                    shared_file.flush()
                    fd = shared_file.fileno()
                    try:
                        uuid = await backend.save_file(str(filename), fd)
                    except sdbus.DbusFailedError as err:
                        print(f"error awaiting backend.save_file: {err}")
                        await queue.put((Status.DONE, "failed"))
                        return
                    else:
                        await queue.put((Status.STARTING, uuid))

            async with asyncio.TaskGroup() as group:
                group.create_task(wait_for_done())
                group.create_task(share_file(content))
                # TODO: this times out if we need a lot of time
                while True:
                    event: tuple[Status, str] = await queue.get()
                    print("got event:", event)
                    # if request.is_disconnected():
                    #     print("client disconnected ...")
                    #     break

                    state, msg = event
                    yield json.dumps({"state": state, "msg": msg})

                    queue.task_done()
                    if state == Status.DONE:
                        print("done")
                        await asyncio.sleep(1)
                        break

    # TODO: make this two separate things - one for the post request and one streaming response for the status
    return EventSourceResponse(event_generator(), send_timeout=5)


@router.post("/system/power/reboot")
async def reboot(current_user: User = Depends(get_current_active_user)):
    with contextlib.closing(sdbus.sd_bus_open_system()) as system_bus:
        backend = YavdrSystemBackend.new_proxy(YAVDR_BACKEND_INTERFACE, "/", system_bus)
        await backend.reboot()


@router.post("/system/power/poweroff")
async def poweroff(current_user: User = Depends(get_current_active_user)):
    with contextlib.closing(sdbus.sd_bus_open_system()) as system_bus:
        backend = YavdrSystemBackend.new_proxy(YAVDR_BACKEND_INTERFACE, "/", system_bus)
        await backend.poweroff()
