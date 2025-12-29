from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrChannelInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.channel",
):
    @dbus_method_async(
        result_signature="i",
    )
    async def count(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="is",
    )
    async def current(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ii",
        result_signature="a(is)",
    )
    async def get_from_to(
        self,
        from_index: int,
        to_index: int,
    ) -> List[Tuple[int, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="a(is)is",
    )
    async def list(
        self,
        option: str,
    ) -> Tuple[List[Tuple[int, str]], int, str]:
        raise NotImplementedError
