from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class OrgYavdrPulseDBusCtlInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.yavdr.PulseDBusCtl",
):
    @dbus_method_async(
        input_signature="",
        result_signature="(a(ssibiadsb)s)",
        method_name="ListSinks",
    )
    async def list_sinks(
        self,
    ) -> Tuple[List[Tuple[str, str, int, bool, int, List[float], str, bool]], str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s", result_signature="b", method_name="SetDefaultSink"
    )
    async def set_default_sink(
        self,
        sink_name: str,
    ) -> bool:
        raise NotImplementedError
