from __future__ import annotations

from typing import Any, List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrSetupInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.setup",
):
    @dbus_method_async(
        result_signature="a(sv)",
    )
    async def list(
        self,
    ) -> List[Tuple[str, Tuple[str, Any]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="vis",
    )
    async def get(
        self,
        name: str,
    ) -> Tuple[Tuple[str, Any], int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sv",
        result_signature="is",
    )
    async def set(
        self,
        name: str,
        value: Tuple[str, Any],
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def delete(
        self,
        name: str,
        method_name="del"
    ) -> Tuple[int, str]:
        raise NotImplementedError
