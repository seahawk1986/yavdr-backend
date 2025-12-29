from __future__ import annotations

from pydantic import BaseModel
from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)
import sdbus


class OutputProfile(BaseModel):
    name: str


class OrgYavdrPulseDBusCtlInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.yavdr.PulseDBusCtl",
):

    @sdbus.dbus_method_async(
        result_signature='a(ssa(ss)s)',
        flags=sdbus.DbusUnprivilegedFlag,
    )
    async def list_output_profiles(self) -> list[tuple[str, str, list[tuple[str, str]], str]]:
        raise NotImplementedError

    @sdbus.dbus_method_async(
        input_signature="ss",
        result_signature="b",
        flags=sdbus.DbusUnprivilegedFlag
    )
    async def set_profile(self, card_name: str, profile_name: str) -> bool:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="",
        result_signature="a(ssiibiadsb)s",
        method_name="ListSinks",
    )
    async def list_sinks(
        self,
    ) -> tuple[list[tuple[str, str, int, int, bool, int, list[float], str, bool]], str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s", result_signature="b", method_name="SetDefaultSink"
    )
    async def set_default_sink(
        self,
        sink_name: str,
    ) -> bool:
        raise NotImplementedError
