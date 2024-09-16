from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_signal_async,
)


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
