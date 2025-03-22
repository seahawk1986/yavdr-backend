from enum import Enum
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sdbus
import sdbus.exceptions
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from .auth import get_current_active_user, User
from app.interfaces.pulsedbusctl import OrgYavdrPulseDBusCtlInterface


router = APIRouter()

# bus = sdbus.sd_bus_open_system()


# TODO: Move to common file (duplicate in vdr.py and others)
class Message(BaseModel):
    msg: str


class Sink(BaseModel):
    sink: str


class PortActiveEnum(str, Enum):
    yes = "yes"
    no = "no"
    unknown = "unknown"


class PulseSink(BaseModel):
    device: str
    device_name: str
    index: int
    muted: bool
    number_of_channels: int
    volume_values: List[float]  # array of doubles
    port_active: PortActiveEnum  # string one of ["yes", "no", "unknown"]
    is_default_sink: bool


class PulseResponse(BaseModel):
    pulse_devices: List[PulseSink]
    default_sink: str


# @pydbus_error_handler
@router.get("/audio/list_pulseaudio_sinks", response_model=PulseResponse)
async def list_pulseaudio_sinks():  # *, current_user: User = Depends(get_current_active_user)):
    pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
        "org.yavdr.PulseDBusCtl",
        "/org/yavdr/PulseDBusCtl",
        bus=sdbus.sd_bus_open_system(),
    )
    devices = []
    sinks, default_sink = await pulsectl.list_sinks()
    for s in sinks:
        (
            device,
            device_name,
            index,
            muted,
            number_of_channels,
            volume_values,
            port_active,
            is_default_sink,
        ) = s
        devices.append(
            PulseSink(
                device=device,
                device_name=device_name,
                index=index,
                muted=muted,
                number_of_channels=number_of_channels,
                volume_values=volume_values,
                port_active=PortActiveEnum(port_active),
                is_default_sink=is_default_sink,
            )
        )
    return PulseResponse(pulse_devices=devices, default_sink=default_sink)


@router.post(
    "/audio/set_default_pulseaudio_sink",
    responses={
        HTTP_200_OK: {
            "model": Message,
            "description": "set default audio device successfully",
        },
        HTTP_400_BAD_REQUEST: {"model": Message, "description": "invalid device"},
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": Message,
            "description": "pulseaudio or dbus_pulsectl is not available",
        },
    },
)
async def set_default_pulseaudio_sink(
    *, default_sink: Sink, current_user: User = Depends(get_current_active_user)
):
    bus = sdbus.sd_bus_open_system()
    pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
        "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl", bus=bus
    )
    sink = default_sink.sink

    try:
        if await pulsectl.set_default_sink(sink_name=sink):
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={"msg": f"set {sink} as default sink"},
            )
        else:
            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"msg": f"invalid device {sink}"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=HTTP_503_SERVICE_UNAVAILABLE, content={"msg": f"Error: {e}"}
        )
