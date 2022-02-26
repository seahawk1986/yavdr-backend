from enum import Enum
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from .auth import get_current_active_user, User
from tools.dbus import pydbus_error_handler
from tools.sound import get_pulseaudio_sinks, set_pulseaudio_default_sink

router = APIRouter()


# TODO: Move to common file (duplicate in vdr.py and others)
class Message(BaseModel):
    msg: str


class Sink(BaseModel):
    Sink: str


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


@pydbus_error_handler
@router.get("/audio/list_pulseaudio_sinks", response_model=List[PulseSink])
def list_pulseaudio_sinks(current_user: User = Depends(get_current_active_user)):
    result = []
    sinks = get_pulseaudio_sinks()
    for s in sinks:
        result.append(PulseSink(**{key: s[i] for i, key in enumerate(PulseSink.__fields__.keys())}))
    return result


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
@pydbus_error_handler("dbus-pulsectl")
def set_default_pulseaudio_sink(
    *, default_sink: Sink, current_user: User = Depends(get_current_active_user)
):
    if set_pulseaudio_default_sink(default_sink.Sink):
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"msg": f"set {default_sink.Sink} as default sink"},
        )
    else:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"msg": f"invalid device {default_sink.Sink}"},
        )
