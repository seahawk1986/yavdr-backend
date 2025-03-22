from __future__ import annotations

from typing import Any, List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    DbusPropertyEmitsInvalidationFlag,
    DbusUnprivilegedFlag,
    dbus_method_async,
    dbus_property_async,
)


class OrgFreedesktopSystemd1ServiceInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.systemd1.Service",
):
    @dbus_method_async(
        input_signature="ssbb",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def bind_mount(
        self,
        source: str,
        destination: str,
        read_only: bool,
        mkdir: bool,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ssbba(ss)",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def mount_image(
        self,
        source: str,
        destination: str,
        read_only: bool,
        mkdir: bool,
        options: List[Tuple[str, str]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(suuutuusu)",
        result_args_names=('entries',),
        flags=DbusUnprivilegedFlag,
    )
    async def dump_file_descriptor_store(
        self,
    ) -> List[Tuple[str, int, int, int, int, int, int, str, int]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(sus)",
        result_args_names=('processes',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_processes(
        self,
    ) -> List[Tuple[str, int, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sau",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def attach_processes(
        self,
        subcgroup: str,
        pids: List[int],
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def type(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def exit_type(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def restart(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def restart_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def pidfile(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def notify_access(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def restart_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def restart_steps(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def restart_max_delay_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def restart_usec_next(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def timeout_start_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def timeout_stop_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def timeout_abort_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def timeout_start_failure_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def timeout_stop_failure_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def runtime_max_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def runtime_randomized_extra_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def watchdog_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def watchdog_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def watchdog_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def root_directory_start_only(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def remain_after_exit(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def guess_main_pid(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(aiai)",
        flags=DbusPropertyConstFlag,
    )
    def restart_prevent_exit_status(self) -> Tuple[List[int], List[int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(aiai)",
        flags=DbusPropertyConstFlag,
    )
    def restart_force_exit_status(self) -> Tuple[List[int], List[int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(aiai)",
        flags=DbusPropertyConstFlag,
    )
    def success_exit_status(self) -> Tuple[List[int], List[int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def main_pid(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def control_pid(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def bus_name(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def file_descriptor_store_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def nfile_descriptor_store(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def file_descriptor_store_preserve(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def status_text(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def status_errno(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def result(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def reload_result(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def clean_result(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def usbfunction_descriptors(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def usbfunction_strings(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def uid(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def gid(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def nrestarts(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def oompolicy(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sst)",
        flags=DbusPropertyConstFlag,
    )
    def open_file(self) -> List[Tuple[str, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def reload_signal(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def exec_main_start_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def exec_main_start_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def exec_main_exit_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def exec_main_exit_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def exec_main_pid(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def exec_main_code(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def exec_main_status(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasbttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_condition(self) -> List[Tuple[str, List[str], bool, int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasasttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_condition_ex(self) -> List[Tuple[str, List[str], List[str], int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasbttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_start_pre(self) -> List[Tuple[str, List[str], bool, int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasasttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_start_pre_ex(self) -> List[Tuple[str, List[str], List[str], int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasbttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_start(self) -> List[Tuple[str, List[str], bool, int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasasttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_start_ex(self) -> List[Tuple[str, List[str], List[str], int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasbttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_start_post(self) -> List[Tuple[str, List[str], bool, int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasasttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_start_post_ex(self) -> List[Tuple[str, List[str], List[str], int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasbttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_reload(self) -> List[Tuple[str, List[str], bool, int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasasttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_reload_ex(self) -> List[Tuple[str, List[str], List[str], int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasbttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_stop(self) -> List[Tuple[str, List[str], bool, int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasasttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_stop_ex(self) -> List[Tuple[str, List[str], List[str], int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasbttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_stop_post(self) -> List[Tuple[str, List[str], bool, int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sasasttttuii)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def exec_stop_post_ex(self) -> List[Tuple[str, List[str], List[str], int, int, int, int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def slice(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def control_group(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def control_group_id(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_current(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_peak(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_swap_current(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_swap_peak(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_zswap_current(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_available(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def cpuusage_nsec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
    )
    def effective_cpus(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
    )
    def effective_memory_nodes(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def tasks_current(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def ipingress_bytes(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def ipingress_packets(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def ipegress_bytes(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def ipegress_packets(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def ioread_bytes(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def ioread_operations(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def iowrite_bytes(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def iowrite_operations(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def delegate(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
    )
    def delegate_controllers(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def delegate_subgroup(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def cpuaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def cpuweight(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_cpuweight(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def cpushares(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_cpushares(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def cpuquota_per_sec_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def cpuquota_period_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
    )
    def allowed_cpus(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
    )
    def startup_allowed_cpus(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
    )
    def allowed_memory_nodes(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
    )
    def startup_allowed_memory_nodes(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def ioaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def ioweight(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_ioweight(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def iodevice_weight(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def ioread_bandwidth_max(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def iowrite_bandwidth_max(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def ioread_iopsmax(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def iowrite_iopsmax(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def iodevice_latency_target_usec(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def block_ioaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def block_ioweight(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_block_ioweight(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def block_iodevice_weight(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def block_ioread_bandwidth(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(st)",
    )
    def block_iowrite_bandwidth(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def memory_accounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def default_memory_low(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def default_startup_memory_low(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def default_memory_min(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_min(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_low(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_memory_low(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_high(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_memory_high(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_memory_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_swap_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_memory_swap_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_zswap_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def startup_memory_zswap_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_limit(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def device_policy(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ss)",
    )
    def device_allow(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def tasks_accounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def tasks_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def ipaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(iayu)",
    )
    def ipaddress_allow(self) -> List[Tuple[int, bytes, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(iayu)",
    )
    def ipaddress_deny(self) -> List[Tuple[int, bytes, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
    )
    def ipingress_filter_path(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
    )
    def ipegress_filter_path(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
    )
    def disable_controllers(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def managed_oomswap(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def managed_oommemory_pressure(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def managed_oommemory_pressure_limit(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def managed_oompreference(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ss)",
    )
    def bpfprogram(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(iiqq)",
    )
    def socket_bind_allow(self) -> List[Tuple[int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(iiqq)",
    )
    def socket_bind_deny(self) -> List[Tuple[int, int, int, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bas)",
    )
    def restrict_network_interfaces(self) -> Tuple[bool, List[str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def memory_pressure_watch(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def memory_pressure_threshold_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(iiss)",
    )
    def nftset(self) -> List[Tuple[int, int, str, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def coredump_receive(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def environment(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sb)",
        flags=DbusPropertyConstFlag,
    )
    def environment_files(self) -> List[Tuple[str, bool]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def pass_environment(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def unset_environment(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def umask(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_cpu(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_cpusoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_fsize(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_fsizesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_data(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_datasoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_stack(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_stacksoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_core(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_coresoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_rss(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_rsssoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_nofile(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_nofilesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_as(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_assoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_nproc(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_nprocsoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_memlock(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_memlocksoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_locks(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_lockssoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_sigpending(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_sigpendingsoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_msgqueue(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_msgqueuesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_nice(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_nicesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_rtprio(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_rtpriosoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_rttime(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def limit_rttimesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def working_directory(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def root_directory(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def root_image(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ss)",
        flags=DbusPropertyConstFlag,
    )
    def root_image_options(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
        flags=DbusPropertyConstFlag,
    )
    def root_hash(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def root_hash_path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
        flags=DbusPropertyConstFlag,
    )
    def root_hash_signature(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def root_hash_signature_path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def root_verity(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def root_ephemeral(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def extension_directories(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sba(ss))",
        flags=DbusPropertyConstFlag,
    )
    def extension_images(self) -> List[Tuple[str, bool, List[Tuple[str, str]]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ssba(ss))",
        flags=DbusPropertyConstFlag,
    )
    def mount_images(self) -> List[Tuple[str, str, bool, List[Tuple[str, str]]]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def oomscore_adjust(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def coredump_filter(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def nice(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def ioscheduling_class(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def ioscheduling_priority(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def cpuscheduling_policy(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def cpuscheduling_priority(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
        flags=DbusPropertyConstFlag,
    )
    def cpuaffinity(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def cpuaffinity_from_numa(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def numapolicy(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
        flags=DbusPropertyConstFlag,
    )
    def numamask(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def timer_slack_nsec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def cpuscheduling_reset_on_fork(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def non_blocking(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def standard_input(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def standard_input_file_descriptor_name(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
        flags=DbusPropertyConstFlag,
    )
    def standard_input_data(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def standard_output(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def standard_output_file_descriptor_name(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def standard_error(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def standard_error_file_descriptor_name(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def ttypath(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def ttyreset(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def ttyvhangup(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def ttyvtdisallocate(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="q",
        flags=DbusPropertyConstFlag,
    )
    def ttyrows(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="q",
        flags=DbusPropertyConstFlag,
    )
    def ttycolumns(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def syslog_priority(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def syslog_identifier(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def syslog_level_prefix(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def syslog_level(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def syslog_facility(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def log_level_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def log_rate_limit_interval_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def log_rate_limit_burst(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="aay",
        flags=DbusPropertyConstFlag,
    )
    def log_extra_fields(self) -> List[bytes]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(bs)",
        flags=DbusPropertyConstFlag,
    )
    def log_filter_patterns(self) -> List[Tuple[bool, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def log_namespace(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def secure_bits(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def capability_bounding_set(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def ambient_capabilities(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def user(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def group(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def dynamic_user(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def set_login_environment(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def remove_ipc(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(say)",
        flags=DbusPropertyConstFlag,
    )
    def set_credential(self) -> List[Tuple[str, bytes]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(say)",
        flags=DbusPropertyConstFlag,
    )
    def set_credential_encrypted(self) -> List[Tuple[str, bytes]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ss)",
        flags=DbusPropertyConstFlag,
    )
    def load_credential(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ss)",
        flags=DbusPropertyConstFlag,
    )
    def load_credential_encrypted(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def import_credential(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def supplementary_groups(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def pamname(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def read_write_paths(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def read_only_paths(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def inaccessible_paths(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def exec_paths(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def no_exec_paths(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def exec_search_path(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def mount_flags(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def private_tmp(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def private_devices(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def protect_clock(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def protect_kernel_tunables(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def protect_kernel_modules(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def protect_kernel_logs(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def protect_control_groups(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def private_network(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def private_users(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def private_mounts(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def private_ipc(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def protect_home(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def protect_system(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def same_process_group(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def utmp_identifier(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def utmp_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bs)",
        flags=DbusPropertyConstFlag,
    )
    def selinux_context(self) -> Tuple[bool, str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bs)",
        flags=DbusPropertyConstFlag,
    )
    def app_armor_profile(self) -> Tuple[bool, str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bs)",
        flags=DbusPropertyConstFlag,
    )
    def smack_process_label(self) -> Tuple[bool, str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def ignore_sigpipe(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def no_new_privileges(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bas)",
        flags=DbusPropertyConstFlag,
    )
    def system_call_filter(self) -> Tuple[bool, List[str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def system_call_architectures(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def system_call_error_number(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bas)",
        flags=DbusPropertyConstFlag,
    )
    def system_call_log(self) -> Tuple[bool, List[str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def personality(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def lock_personality(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bas)",
        flags=DbusPropertyConstFlag,
    )
    def restrict_address_families(self) -> Tuple[bool, List[str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sst)",
        flags=DbusPropertyConstFlag,
    )
    def runtime_directory_symlink(self) -> List[Tuple[str, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def runtime_directory_preserve(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def runtime_directory_mode(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def runtime_directory(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sst)",
        flags=DbusPropertyConstFlag,
    )
    def state_directory_symlink(self) -> List[Tuple[str, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def state_directory_mode(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def state_directory(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sst)",
        flags=DbusPropertyConstFlag,
    )
    def cache_directory_symlink(self) -> List[Tuple[str, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def cache_directory_mode(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def cache_directory(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sst)",
        flags=DbusPropertyConstFlag,
    )
    def logs_directory_symlink(self) -> List[Tuple[str, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def logs_directory_mode(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def logs_directory(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def configuration_directory_mode(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def configuration_directory(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def timeout_clean_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def memory_deny_write_execute(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def restrict_realtime(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def restrict_suidsgid(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def restrict_namespaces(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(bas)",
        flags=DbusPropertyConstFlag,
    )
    def restrict_file_systems(self) -> Tuple[bool, List[str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ssbt)",
        flags=DbusPropertyConstFlag,
    )
    def bind_paths(self) -> List[Tuple[str, str, bool, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ssbt)",
        flags=DbusPropertyConstFlag,
    )
    def bind_read_only_paths(self) -> List[Tuple[str, str, bool, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ss)",
        flags=DbusPropertyConstFlag,
    )
    def temporary_file_system(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def mount_apivfs(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def keyring_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def protect_proc(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def proc_subset(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def protect_hostname(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def memory_ksm(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def network_namespace_path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def ipcnamespace_path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def root_image_policy(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def mount_image_policy(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def extension_image_policy(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def kill_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def kill_signal(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def restart_kill_signal(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def final_kill_signal(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def send_sigkill(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def send_sighup(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def watchdog_signal(self) -> int:
        raise NotImplementedError


class OrgFreedesktopSystemd1UnitInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.systemd1.Unit",
):
    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def start(
        self,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def stop(
        self,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def reload(
        self,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def restart(
        self,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def try_restart(
        self,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def reload_or_restart(
        self,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def reload_or_try_restart(
        self,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="uososa(uosos)",
        result_args_names=('job_id', 'job_path', 'unit_id', 'unit_path', 'job_type', 'affected_jobs'),
        flags=DbusUnprivilegedFlag,
    )
    async def enqueue_job(
        self,
        job_type: str,
        job_mode: str,
    ) -> Tuple[int, str, str, str, str, List[Tuple[int, str, str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="si",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def kill(
        self,
        whom: str,
        signal: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sii",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def queue_signal(
        self,
        whom: str,
        signal: int,
        value: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def reset_failed(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ba(sv)",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def set_properties(
        self,
        runtime: bool,
        properties: List[Tuple[str, Tuple[str, Any]]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def ref(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def unref(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def clean(
        self,
        mask: List[str],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def freeze(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def thaw(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def id(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def names(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def following(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def requires(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def requisite(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def wants(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def binds_to(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def part_of(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def upholds(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def required_by(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def requisite_of(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def wanted_by(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def bound_by(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def upheld_by(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def consists_of(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def conflicts(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def conflicted_by(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def before(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def after(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def on_success(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def on_success_of(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def on_failure(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def on_failure_of(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def triggers(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def triggered_by(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def propagates_reload_to(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def reload_propagated_from(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def propagates_stop_to(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def stop_propagated_from(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def joins_namespace_of(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def slice_of(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def requires_mounts_for(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def documentation(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def description(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def access_selinux_context(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def load_state(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def active_state(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def freezer_state(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def sub_state(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def fragment_path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def source_path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def drop_in_paths(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def unit_file_state(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def unit_file_preset(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def state_change_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def state_change_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def inactive_exit_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def inactive_exit_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def active_enter_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def active_enter_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def active_exit_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def active_exit_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def inactive_enter_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def inactive_enter_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def can_start(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def can_stop(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def can_reload(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def can_isolate(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def can_clean(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def can_freeze(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(uo)",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def job(self) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def stop_when_unneeded(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def refuse_manual_start(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def refuse_manual_stop(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def allow_isolate(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def default_dependencies(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def survive_final_kill_signal(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def on_success_job_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def on_failure_job_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def ignore_on_isolate(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def need_daemon_reload(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
    )
    def markers(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def job_timeout_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def job_running_timeout_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def job_timeout_action(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def job_timeout_reboot_argument(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def condition_result(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def assert_result(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def condition_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def condition_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def assert_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def assert_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sbbsi)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def conditions(self) -> List[Tuple[str, bool, bool, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(sbbsi)",
        flags=DbusPropertyEmitsInvalidationFlag,
    )
    def asserts(self) -> List[Tuple[str, bool, bool, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="(ss)",
        flags=DbusPropertyConstFlag,
    )
    def load_error(self) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def transient(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def perpetual(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def start_limit_interval_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def start_limit_burst(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def start_limit_action(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def failure_action(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def failure_action_exit_status(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def success_action(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def success_action_exit_status(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def reboot_argument(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="ay",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def invocation_id(self) -> bytes:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def collect_mode(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
    )
    def refs(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="a(ss)",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def activation_details(self) -> List[Tuple[str, str]]:
        raise NotImplementedError

