from __future__ import annotations

import asyncio
from contextlib import closing
from enum import StrEnum
from typing import AsyncGenerator, List, Tuple

from pydantic import BaseModel

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_signal_async,
)
import sdbus


class DeTvdrVdrStatusInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.status",
):
    @dbus_method_async(
        result_signature="ssb",
    )
    async def is_replaying(
        self,
    ) -> Tuple[str, str, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="s",
    )
    def channel_change(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ss",
    )
    def timer_change(self) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="iib",
    )
    def channel_switch(self) -> Tuple[int, int, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="issb",
    )
    def recording(self) -> Tuple[int, str, str, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ssb",
    )
    def replaying(self) -> Tuple[str, str, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ib",
    )
    def set_volume(self) -> Tuple[int, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ias",
    )
    def set_audio_track(self) -> Tuple[int, List[str]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="i",
    )
    def set_audio_channel(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ias",
    )
    def set_subtitle_track(self) -> Tuple[int, List[str]]:
        raise NotImplementedError


class ChannelSwitch(BaseModel):
    DeviceNumber: int
    ChannelNumber: int
    LiveView: bool


class Recording(BaseModel):
    DeviceNumber: int
    Name: str
    FileName: str
    On: bool


class Replaying(BaseModel):
    Name: str
    FileName: str
    on: bool


class SetAudioChannel(BaseModel):
    AudioChannel: int


class SetAudioTrack(BaseModel):
    Index: int
    Tracks: list[str]


class SetSubtitleTrack(BaseModel):
    Index: int
    Tracks: list[str]


class SetVolume(BaseModel):
    Volume: int
    Absolute: bool


class TimerChangeEnum(StrEnum):
    tcMod = "tcMod"
    tcAdd = "tcAdd"
    tcDel = "tcDel"


class TimerChange(BaseModel):
    Timer: str
    Change: TimerChangeEnum


SignalType = (
    ChannelSwitch
    | Recording
    | Replaying
    | SetAudioChannel
    | SetAudioTrack
    | SetSubtitleTrack
    | SetVolume
    | TimerChange
)

SignalLookup = {c.__name__: c for c in SignalType.__args__}


async def signal_generator() -> AsyncGenerator[SignalType, None]:
    bus = sdbus.sd_bus_open_system()
    msg_queue = asyncio.Queue()

    def put_msg(msg):
        msg_queue.put_nowait(msg)

    with closing(
        await bus.match_signal_async(
            "de.tvdr.vdr", "/Status", "de.tvdr.vdr.status", None, put_msg
        )
    ):
        while True:
            msg = await msg_queue.get()
            event = msg.parse_to_tuple()
            event_type = SignalLookup[msg.member]
            result: SignalType = event_type(
                **{
                    key: event[i]
                    for i, key in enumerate(event_type.model_fields.keys())
                }
            )
            yield result
