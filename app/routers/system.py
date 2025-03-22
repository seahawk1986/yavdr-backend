# Module for system information (and possible operations)
import json
import sys
import sdbus
from threading import Lock
from typing import Mapping

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

from app.interfaces.system_backend import YavdrSystemBackend, Status, YAVDR_BACKEND_INTERFACE
# from interfaces.system_backend import YAVDR_BACKEND_INTERFACE


router = APIRouter()
ANSIBLE_LOCK = Lock()


class Playbook(BaseModel):
    playbook: str
    options: Mapping

@router.get("/system/playbook/{name}")
async def run_playbook(name: str, request: Request):
    """forward dbus2vdr's signals as Server Side Events"""

    system_bus = sdbus.sd_bus_open_system()
    backend_connection = YavdrSystemBackend(system_bus).new_proxy(
        YAVDR_BACKEND_INTERFACE, "/", 
    )

    async def event_generator():
        job_uuid = await backend_connection.rescan_displays()
        runner_ident = None
        async for event in backend_connection.ansible_event:
            # print(f"{event}")
            message_type, message = event
            # print(f"{message_type} - {message}")
            if await request.is_disconnected():
                break
            if message_type == Status.DONE:
                job_uuid = None
                runner_ident = None
                yield message
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
