from __future__ import annotations

from typing import Any, List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrEpgInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.epg",
):
    @dbus_method_async(
        input_signature="i",
        result_signature="is",
    )
    async def disable_scanner(
        self,
        eitdisabletime: int,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="is",
    )
    async def enable_scanner(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="si",
        result_signature="is",
    )
    async def clear_epg(
        self,
        channel: str,
        eitdisabletime: int,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_signature="is",
    )
    async def put_entry(
        self,
        entryline: List[str],
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def put_file(
        self,
        filename: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="isaa(sv)",
    )
    async def now(
        self,
        channel: str,
    ) -> Tuple[int, str, List[List[Tuple[str, Tuple[str, Any]]]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="isaa(sv)",
    )
    async def next(
        self,
        channel: str,
    ) -> Tuple[int, str, List[List[Tuple[str, Tuple[str, Any]]]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="st",
        result_signature="isaa(sv)",
    )
    async def at(
        self,
        channel: str,
        time: int,
    ) -> Tuple[int, str, List[List[Tuple[str, Tuple[str, Any]]]]]:
        raise NotImplementedError
