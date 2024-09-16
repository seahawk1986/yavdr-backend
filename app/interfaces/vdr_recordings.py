from __future__ import annotations

from typing import Any, List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrRecordingInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.recording",
):
    @dbus_method_async(
        result_signature="is",
    )
    async def update(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="v",
        result_signature="(ia(sv))",
    )
    async def get(
        self,
        number_or_path: Tuple[str, Any],
    ) -> Tuple[int, List[Tuple[str, Tuple[str, Any]]]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(ia(sv))",
    )
    async def list(
        self,
    ) -> List[Tuple[int, List[Tuple[str, Tuple[str, Any]]]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="vv",
        result_signature="is",
    )
    async def play(
        self,
        number_or_path: Tuple[str, Any],
        begin: Tuple[str, Any],
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="vs",
        result_signature="is",
    )
    async def change_name(
        self,
        number_or_path: Tuple[str, Any],
        newname: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError
