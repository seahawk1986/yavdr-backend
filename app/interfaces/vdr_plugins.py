from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
)


# class DeTvdrVdrPluginInterface(
#     DbusInterfaceCommonAsync,
#     interface_name="de.tvdr.vdr.plugin",
# ):
#     @dbus_method_async(
#         result_signature="a(ss)",
#     )
#     async def list(
#         self,
#     ) -> List[Tuple[str, str]]:
#         raise NotImplementedError


class DeTvdrVdrPluginmanagerInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.pluginmanager",
):
    @dbus_method_async(
        result_signature="a(ss)",
    )
    async def list(
        self,
    ) -> List[Tuple[str, str]]:
        raise NotImplementedError
