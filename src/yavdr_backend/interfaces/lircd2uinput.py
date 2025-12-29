from __future__ import annotations

from typing import Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeYavdrLircd2uinputInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.yavdr.lircd2uinput",
):
    @dbus_method_async(
        input_signature="ss",
        result_signature="bs",
        method_name="add_socket"
    )
    async def add_socket(
        self,
        socket_path: str,
        r_suffix: str,
    ) -> Tuple[bool, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="bs",
        method_name="remove_socket"
    )
    async def remove_socket(
        self,
        socket_path: str,
    ) -> Tuple[bool, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="bs",
        method_name="emit_key",
    )
    async def emit_key(
        self,
        keyname: str,
    ) -> Tuple[bool, str]:
        raise NotImplementedError
