from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrSkinInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.skin",
):
    @dbus_method_async(
        result_signature="i(iss)",
    )
    async def current_skin(
        self,
    ) -> Tuple[int, Tuple[int, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="ia(iss)",
    )
    async def list_skins(
        self,
    ) -> Tuple[int, List[Tuple[int, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def set_skin(
        self,
        name: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def queue_message(
        self,
        message_text: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError
