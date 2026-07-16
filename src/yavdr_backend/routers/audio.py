from contextlib import closing
from enum import Enum
import sys
from typing import Annotated, NamedTuple

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import sdbus
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)


from .auth import get_current_active_user, User

from yavdr_pulse_dbusctl.main import (
    PulseDBusControl as OrgYavdrPulseDBusCtlInterface,
    Sink as TupleSink,
    alsa,
)


router = APIRouter()

# bus = sdbus.sd_bus_open_system()


# TODO: Move to common file (duplicate in vdr.py and others)
class Message(BaseModel):
    msg: str


class SinkData(BaseModel):
    default_sink: str
    card_name: str


class PortActiveEnum(str, Enum):
    yes = "yes"
    no = "no"
    unknown = "unknown"


class PulseSink(BaseModel):
    device: str
    device_name: str
    index: int
    card: int
    card_name: str
    muted: bool
    number_of_channels: int
    volume_values: list[float]  # array of doubles
    port_active: PortActiveEnum  # string one of ["yes", "no", "unknown"]
    is_default_sink: bool = False


class PulseResponse(BaseModel):
    pulse_devices: list[PulseSink]
    default_sink: str


# @pydbus_error_handler
@router.get("/audio/list_pulseaudio_sinks", response_model=PulseResponse)
async def list_pulseaudio_sinks(
    current_user: User = Depends(get_current_active_user),
) -> PulseResponse:
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
                    index=s.idx,
                    card=s.card,
                    card_name=s.card_name,
                    muted=s.is_muted,
                    number_of_channels=s.channel_count,
                    volume_values=s.volume_values,
                    port_active=PortActiveEnum(s.port_active),
                    is_default_sink=s.is_default_sink,
                )
            )
        return PulseResponse(
            pulse_devices=sorted(devices, key=lambda x: x.device),
            default_sink=default_sink,
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
    data: SinkData,
    current_user: User = Depends(get_current_active_user),
) -> JSONResponse:

    default_sink = data.default_sink
    card_name = data.card_name

    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
            "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl", bus=bus
        )

        print(f"set_default_pulseaudio_sink: sink_name={default_sink}, {card_name=}")

        try:
            if await pulsectl.set_default_sink(
                sink_name=default_sink, card_name=card_name
            ):
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={"msg": f"set {default_sink} as default sink"},
                )
            else:
                return JSONResponse(
                    status_code=HTTP_400_BAD_REQUEST,
                    content={"msg": f"invalid device {default_sink}"},
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
    print(f"set output profile: {data}")
    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
            "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl", bus=bus
        )
        return await pulsectl.set_profile(data.card_name, data.profile_name)


class SystemVolumeData(BaseModel):
    device: str
    volume: Annotated[float, Field(ge=0.0, le=1.53)]


@router.post("/system/audio/volume")
async def set_volume(
    data: SystemVolumeData, current_user: User = Depends(get_current_active_user)
) -> bool:
    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = OrgYavdrPulseDBusCtlInterface.new_proxy(
            "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl", bus=bus
        )
        return await pulsectl.set_volume(data.device, data.volume)


class AlsaMixer(BaseModel):
    name: str
    card_idx: int
    card_name: str
    volume: int
    volume_range: tuple[int, int]
    is_muted: bool


class AlsaMixerTuple(NamedTuple):
    name: str
    card_idx: int
    card_name: str
    volume: int
    volume_range: tuple[int, int]
    is_muted: bool


@router.get("/system/audio/alsa_mixers")
async def list_alsa_mixer(
    current_user: User = Depends(get_current_active_user),
) -> list[AlsaMixer]:
    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = alsa.AlsaDBusControl.new_proxy(
            "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl/Alsa", bus=bus
        )

        mixer_data: list[AlsaMixer] = list()
        mixers = await pulsectl.list_alsa_mixers()
        for m in mixers:
            m = AlsaMixerTuple(*m)
            mixer_data.append(AlsaMixer.model_validate(m._asdict()))
        return mixer_data


class AlsaMixerData(BaseModel):
    mixer_name: str
    card_idx: int
    volume: int | float
    muted: bool


@router.post("/system/audio/alsa_mixer_setting")
async def set_alsa_mixer(
    data: AlsaMixerData, current_user: User = Depends(get_current_active_user)
) -> list[AlsaMixer]:
    with closing(sdbus.sd_bus_open_system()) as bus:
        pulsectl = alsa.AlsaDBusControl.new_proxy(
            "org.yavdr.PulseDBusCtl", "/org/yavdr/PulseDBusCtl/Alsa", bus=bus
        )
        mixer_data: list[AlsaMixer] = list()
        mixers = await pulsectl.set_state(
            data.mixer_name, data.card_idx, int(data.volume), data.muted
        )

        for m in mixers:
            m = AlsaMixerTuple(*m)
            mixer_data.append(AlsaMixer.model_validate(m._asdict()))
        return mixer_data
