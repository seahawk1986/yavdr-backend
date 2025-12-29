from contextlib import closing
from enum import Enum
import sys

from fastapi import APIRouter, Depends
from pydantic import BaseModel
import sdbus
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from .auth import get_current_active_user, User

# from yavdr_backend.interfaces.pulsedbusctl import OrgYavdrPulseDBusCtlInterface
from yavdr_pulse_dbusctl.main import (
    PulseDBusControl as OrgYavdrPulseDBusCtlInterface,
    Sink as TupleSink,
)


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
    card: int
    muted: bool
    number_of_channels: int
    volume_values: list[float]  # array of doubles
    port_active: PortActiveEnum  # string one of ["yes", "no", "unknown"]
    is_default_sink: bool


class PulseResponse(BaseModel):
    pulse_devices: list[PulseSink]
    default_sink: str


# @pydbus_error_handler
@router.get("/audio/list_pulseaudio_sinks", response_model=PulseResponse)
async def list_pulseaudio_sinks() -> (
    PulseResponse
):  # *, current_user: User = Depends(get_current_active_user)):
    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
            "org.yavdr.PulseDBusCtl",
            "/org/yavdr/PulseDBusCtl",
            bus=bus,
        )
        devices: list[PulseSink] = []
        sinks, default_sink = await pulsectl.list_sinks()
        for s in sinks:
            print(f"{s=}, {type(s)=}")
            s = TupleSink(*s)
            print(f"{s.name=}")
            devices.append(
                PulseSink(
                    device=s.name,
                    device_name=s.description,
                    index=s.index,
                    card=s.card,
                    muted=s.is_muted,
                    number_of_channels=s.channel_count,
                    volume_values=s.volume_values,
                    port_active=PortActiveEnum(s.port_active),
                    is_default_sink=s.is_default_sink,
                )
            )
        return PulseResponse(
            pulse_devices=sorted(devices, key=lambda x: x.device), default_sink=default_sink
        )


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
    with closing(sdbus.sd_bus_open_system()) as bus:
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
            print(e, file=sys.stderr)
            return JSONResponse(
                status_code=HTTP_503_SERVICE_UNAVAILABLE, content={"msg": f"Error: {e}"}
            )


class Profile(BaseModel):
    profile_name: str
    profile_description: str


class CardData(BaseModel):
    card_name: str
    card_description: str
    profiles: list[Profile]
    profile_active: str


@router.get("/system/audio/pulseaudio_output_profiles")
async def list_pulseaudio_profiles(
    current_user: User = Depends(get_current_active_user),
) -> list[CardData]:
    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
            "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl", bus=bus
        )

        profile_data = await pulsectl.list_output_profiles()
        cards: list[CardData] = list()
        for card in profile_data:
            card_name, card_description, profiles, profile_active = card
            profile_list: list[Profile] = []
            for p_name, p_description in profiles:
                profile_list.append(
                    Profile(profile_name=p_name, profile_description=p_description)
                )
            cards.append(
                CardData(
                    card_name=card_name,
                    card_description=card_description,
                    profiles=profile_list,
                    profile_active=profile_active,
                )
            )
        return cards


class AudioProfileData(BaseModel):
    card_name: str
    profile_name: str


@router.post("/system/audio/pulseaudio_output_profile")
async def set_card_profile(
    data: AudioProfileData, current_user: User = Depends(get_current_active_user)
) -> bool:
    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
            "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl", bus=bus
        )
        return await pulsectl.set_profile(data.card_name, data.profile_name)
