from __future__ import annotations

from typing import Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


class DeTvdrVdrShutdownInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.shutdown",
):
    @dbus_method_async(
        result_signature="b",
    )
    async def is_user_active(
        self,
    ) -> bool:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="b",
        result_signature="isis",
    )
    async def confirm_shutdown(
        self,
        ignoreuser: bool,
    ) -> Tuple[int, str, int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="b",
    )
    async def manual_start(
        self,
    ) -> bool:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="xs",
    )
    async def next_wakeup_time(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="is",
    )
    async def set_user_inactive(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError
