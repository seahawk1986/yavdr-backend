from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrTimerInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.timer",
):
    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def new(
        self,
        timer: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="i",
        result_signature="is",
    )
    async def delete(
        self,
        number: int,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="as",
    )
    async def list(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(isussiiiissubbb)",
    )
    async def list_detailed(
        self,
    ) -> List[Tuple[int, str, int, str, str, int, int, int, int, str, str, int, bool, bool, bool]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="iiitts",
    )
    async def next(
        self,
    ) -> Tuple[int, int, int, int, int, str]:
        raise NotImplementedError
