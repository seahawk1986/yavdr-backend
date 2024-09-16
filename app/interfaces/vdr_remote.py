from __future__ import annotations

from typing import Any, List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_signal_async,
)


class DeTvdrVdrRemoteInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.remote",
):
    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def call_plugin(
        self,
        plugin_name: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="is",
    )
    async def enable(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="is",
    )
    async def disable(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="b",
    )
    async def status(
        self,
    ) -> bool:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def hit_key(
        self,
        key_name: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_signature="is",
    )
    async def hit_keys(
        self,
        key_names: List[str],
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sas",
        result_signature="is",
    )
    async def ask_user(
        self,
        title: str,
        items: List[str],
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="is",
    )
    async def switch_channel(
        self,
        option: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="ib",
    )
    async def get_volume(
        self,
    ) -> Tuple[int, bool]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="v",
        result_signature="ibis",
    )
    async def set_volume(
        self,
        option: Tuple[str, Any],
    ) -> Tuple[int, bool, int, str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="si",
    )
    def ask_user_select(self) -> Tuple[str, int]:
        raise NotImplementedError
