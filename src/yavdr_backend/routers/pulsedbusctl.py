from enum import Enum
# import logging
# import time
# from typing import List

import sdbus
from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from yavdr_backend.interfaces.pulsedbusctl import OrgYavdrPulseDBusCtlInterface

class Message(BaseModel):
    msg: str

class PortActive(str, Enum):
    ACTIVE = "yes"
    INACTIVE = "no"
    UNKNOWN = "unknown"

class PulseSink(BaseModel):
    # Example output:
    #     ([('alsa_output.pci-0000_01_00.1.hdmi-stereo',
    #    'GP108 High Definition Audio Controller Digital Stereo (HDMI)',
    #    0,
    #    False,
    #    2,
    #    [1.0, 1.0],
    #    'yes',
    #    True),
    #   ('alsa_output.pci-0000_00_1b.0.iec958-stereo',
    #    'Eingebautes Tongerät Digital Stereo (IEC958)',
    #    1,
    #    False,
    #    2,
    #    [1.0, 1.0],
    #    'unknown',
    #    False)],
    #  'alsa_output.pci-0000_01_00.1.hdmi-stereo')
    device_name: str
    description: str
    index: int
    is_muted: bool
    number_of_channels: int
    volume_values: list[float]
    port_is_active: PortActive
    is_default_sink: bool

# pulse_dbus_ctl = OrgYavdrPulseDBusCtlInterface.new_proxy('org.yavdr.PulseDBusCTL', '/org/yavdr/PulseDBusCtl')

router = APIRouter()
system_bus = sdbus.sd_bus_open_system()

@router.get(
        "/system/audio/getSinks"
)
async def get_sinks(*_,):
    pulse_dbus_ctl = OrgYavdrPulseDBusCtlInterface.new_proxy('org.yavdr.PulseDBusCTL', '/org/yavdr/PulseDBusCtl', bus=system_bus)
    response = PulseSink(await pulse_dbus_ctl.list_sinks())
    return JSONResponse(response, status_code=HTTP_200_OK)


@router.post(
    "/system/audio/SetDefaultSink",
    responses={
        HTTP_200_OK: {
            "model": Message,
            "description": "Default sink changed successfully",
        },
        HTTP_400_BAD_REQUEST: {"model": Message, "description": "Invalid sink"},
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": Message,
            "description": "PulseDBusCtl is not available",
        },
    },
)
async def set_default_sink(*, sinkname: str):
    print(f"setting default sink to {sinkname}")
    pulse_dbus_ctl = OrgYavdrPulseDBusCtlInterface.new_proxy('org.yavdr.PulseDBusCTL', '/org/yavdr/PulseDBusCtl')
    success = await pulse_dbus_ctl.set_default_sink(sink_name=sinkname)
    if success:
        return JSONResponse(status_code=HTTP_200_OK, content={"msg": "ok", "sink": sinkname},)
    else:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST, content={"msg": "unknown sink"},
        )
