# Module for system information (and possible operations)
from contextlib import closing
import json
import logging
from pathlib import Path
import sys
from typing import Any
from fastapi.responses import FileResponse
import sdbus
from threading import Lock
from collections.abc import Mapping

from fastapi import APIRouter, Request
from pydantic import BaseModel
from ruamel.yaml import YAML
from sse_starlette import EventSourceResponse

from yavdr_backend.interfaces.system_backend import YavdrSystemBackend, Status, YAVDR_BACKEND_INTERFACE
from yavdr_backend.models.xorg import XorgConfig
# from interfaces.system_backend import YAVDR_BACKEND_INTERFACE


router = APIRouter()
ANSIBLE_LOCK = Lock()


class Playbook(BaseModel):
    playbook: str
    options: Mapping[str, Any]

@router.post("/system/playbook/rescan_displays")
async def run_playbook(request: Request):
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
            runner_ident = None
            async for event in backend_connection.ansible_event:
                # yield event
                message_type, message = event
                # print(f"{message_type} - {message}")
                if await request.is_disconnected():
                    break
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
                        if data.get('event', {}).get('runner_ident') == runner_ident or data.get('status', {}).get('runner_ident'):
                            yield message
                    except json.JSONDecodeError as e:
                        print(e, file=sys.stderr)
                        # yield f"{e}: {message}"
    return EventSourceResponse(event_generator(), send_timeout=5)

@router.get('/system/xorg_config')
async def get_xorg_config() -> XorgConfig:
    config_file = Path('/etc/yavdr/display_config.yml')
    yaml = YAML(typ="safe")
    try:
        with open(config_file) as f:
            data: dict[str, Any] = yaml.load(f) # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
    except IOError:
        fallback_config_file = Path('/etc/ansible/facts.d/xorg_config.fact')
        print(f"fallback to {fallback_config_file=}")
        try:
            with open(fallback_config_file) as f:
                data = json.load(f).get('xorg_config', {})
        except Exception:
            logging.exception("could not load xorg_config, please rescan displays")
            raise

    print(f"{data=}")
    config: XorgConfig = XorgConfig.model_validate(data)
    return config

@router.get('/system/xorg_facts')
async def get_xorg_facts() -> FileResponse:
    return FileResponse('/etc/ansible/facts.d/xorg.fact',
                        headers={"Cache-Control": "no-store"})


@router.get('/system/xrandr_facts')
async def get_xrandr_facts() -> FileResponse:
    return FileResponse('/etc/ansible/facts.d/xrandr.fact',
                        headers={"Cache-Control": "no-store"})

@router.get('/system/drm_facts')
async def get_drm_facts() -> FileResponse:
    return FileResponse('/etc/ansible/facts.d/drm.fact',
                        headers={"Cache-Control": "no-store"})

@router.get('/system/xorg_config')
async def get_xorg_config_facts() -> FileResponse:
    return FileResponse('/etc/ansible/facts.d/xorg_config.fact',
                        headers={"Cache-Control": "no-store"})

@router.post('/system/xorg_config')
async def set_xorg_confg(config: XorgConfig, request: Request) -> EventSourceResponse:
    print("post xorg_config:", config)
    async def event_generator():
        with closing(sdbus.sd_bus_open_system()) as system_bus:
            backend_connection = YavdrSystemBackend(system_bus).new_proxy(
                YAVDR_BACKEND_INTERFACE, "/", system_bus
            )
            await backend_connection.write_display_configuration(config.model_dump_json())
            job_uuid = await backend_connection.set_display_configuration()
            runner_ident = None
            async for event in backend_connection.ansible_event:
                # yield event
                message_type, message = event
                # print(f"{message_type} - {message}")
                if await request.is_disconnected():
                    break
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
                        if data.get('event', {}).get('runner_ident') == runner_ident or data.get('status', {}).get('runner_ident'):
                            yield message
                    except json.JSONDecodeError as e:
                        print(e, file=sys.stderr)
                        # yield f"{e}: {message}"

    return EventSourceResponse(event_generator(), send_timeout=5)