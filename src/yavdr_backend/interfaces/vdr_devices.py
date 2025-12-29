from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrDeviceInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.device",
):
    @dbus_method_async(
        result_signature="iibbs",
    )
    async def get_primary(
        self,
    ) -> Tuple[int, int, bool, bool, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="i",
    )
    async def get_null_device(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="i",
    )
    async def request_primary(
        self,
        index: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(iibbs)",
    )
    async def list(
        self,
    ) -> List[Tuple[int, int, bool, bool, str]]:
        raise NotImplementedError
