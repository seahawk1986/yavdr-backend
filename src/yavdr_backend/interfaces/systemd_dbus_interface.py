from __future__ import annotations

from typing import Any, List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    DbusUnprivilegedFlag,
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
)


class OrgFreedesktopSystemd1ManagerInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.systemd1.Manager",
):
    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('unit',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit(
        self,
        name: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="u",
        result_signature="o",
        result_args_names=('unit',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit_by_pid(
        self,
        pid: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ay",
        result_signature="o",
        result_args_names=('unit',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit_by_invocation_id(
        self,
        invocation_id: bytes,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('unit',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit_by_control_group(
        self,
        cgroup: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="h",
        result_signature="osay",
        result_args_names=('unit', 'unit_id', 'invocation_id'),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit_by_pidfd(
        self,
        pidfd: int,
    ) -> Tuple[str, str, bytes]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="o",
        result_args_names=('unit',),
        flags=DbusUnprivilegedFlag,
    )
    async def load_unit(
        self,
        name: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def start_unit(
        self,
        name: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sst",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def start_unit_with_flags(
        self,
        name: str,
        mode: str,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def start_unit_replace(
        self,
        old_unit: str,
        new_unit: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def stop_unit(
        self,
        name: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def reload_unit(
        self,
        name: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def restart_unit(
        self,
        name: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def try_restart_unit(
        self,
        name: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def reload_or_restart_unit(
        self,
        name: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def reload_or_try_restart_unit(
        self,
        name: str,
        mode: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sss",
        result_signature="uososa(uosos)",
        result_args_names=('job_id', 'job_path', 'unit_id', 'unit_path', 'job_type', 'affected_jobs'),
        flags=DbusUnprivilegedFlag,
    )
    async def enqueue_unit_job(
        self,
        name: str,
        job_type: str,
        job_mode: str,
    ) -> Tuple[int, str, str, str, str, List[Tuple[int, str, str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ssi",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def kill_unit(
        self,
        name: str,
        whom: str,
        signal: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ssii",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def queue_signal_unit(
        self,
        name: str,
        whom: str,
        signal: int,
        value: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sas",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def clean_unit(
        self,
        name: str,
        mask: List[str],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def freeze_unit(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def thaw_unit(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def reset_failed_unit(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sba(sv)",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def set_unit_properties(
        self,
        name: str,
        runtime: bool,
        properties: List[Tuple[str, Tuple[str, Any]]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sssbb",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def bind_mount_unit(
        self,
        name: str,
        source: str,
        destination: str,
        read_only: bool,
        mkdir: bool,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sssbba(ss)",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def mount_image_unit(
        self,
        name: str,
        source: str,
        destination: str,
        read_only: bool,
        mkdir: bool,
        options: List[Tuple[str, str]],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def ref_unit(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def unref_unit(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ssa(sv)a(sa(sv))",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def start_transient_unit(
        self,
        name: str,
        mode: str,
        properties: List[Tuple[str, Tuple[str, Any]]],
        aux: List[Tuple[str, List[Tuple[str, Tuple[str, Any]]]]],
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="a(sus)",
        result_args_names=('processes',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit_processes(
        self,
        name: str,
    ) -> List[Tuple[str, int, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ssau",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def attach_processes_to_unit(
        self,
        unit_name: str,
        subcgroup: str,
        pids: List[int],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def abandon_scope(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="u",
        result_signature="o",
        result_args_names=('job',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_job(
        self,
        id: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="u",
        result_signature="a(usssoo)",
        result_args_names=('jobs',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_job_after(
        self,
        id: int,
    ) -> List[Tuple[int, str, str, str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="u",
        result_signature="a(usssoo)",
        result_args_names=('jobs',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_job_before(
        self,
        id: int,
    ) -> List[Tuple[int, str, str, str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="u",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def cancel_job(
        self,
        id: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def clear_jobs(
        self,
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
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def set_show_status(
        self,
        mode: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(ssssssouso)",
        result_args_names=('units',),
        flags=DbusUnprivilegedFlag,
    )
    async def list_units(
        self,
    ) -> List[Tuple[str, str, str, str, str, str, str, int, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_signature="a(ssssssouso)",
        result_args_names=('units',),
        flags=DbusUnprivilegedFlag,
    )
    async def list_units_filtered(
        self,
        states: List[str],
    ) -> List[Tuple[str, str, str, str, str, str, str, int, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asas",
        result_signature="a(ssssssouso)",
        result_args_names=('units',),
        flags=DbusUnprivilegedFlag,
    )
    async def list_units_by_patterns(
        self,
        states: List[str],
        patterns: List[str],
    ) -> List[Tuple[str, str, str, str, str, str, str, int, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_signature="a(ssssssouso)",
        result_args_names=('units',),
        flags=DbusUnprivilegedFlag,
    )
    async def list_units_by_names(
        self,
        names: List[str],
    ) -> List[Tuple[str, str, str, str, str, str, str, int, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(usssoo)",
        result_args_names=('jobs',),
        flags=DbusUnprivilegedFlag,
    )
    async def list_jobs(
        self,
    ) -> List[Tuple[int, str, str, str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def subscribe(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def unsubscribe(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
        result_args_names=('output',),
        flags=DbusUnprivilegedFlag,
    )
    async def dump(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_signature="s",
        result_args_names=('output',),
        flags=DbusUnprivilegedFlag,
    )
    async def dump_units_matching_patterns(
        self,
        patterns: List[str],
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="h",
        result_args_names=('fd',),
        flags=DbusUnprivilegedFlag,
    )
    async def dump_by_file_descriptor(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_signature="h",
        result_args_names=('fd',),
        flags=DbusUnprivilegedFlag,
    )
    async def dump_units_matching_patterns_by_file_descriptor(
        self,
        patterns: List[str],
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def reload(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def reexecute(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def exit(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def reboot(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def soft_reboot(
        self,
        new_root: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def power_off(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def halt(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def kexec(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ss",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def switch_root(
        self,
        new_root: str,
        init: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def set_environment(
        self,
        assignments: List[str],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def unset_environment(
        self,
        names: List[str],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asas",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def unset_and_set_environment(
        self,
        names: List[str],
        assignments: List[str],
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="ao",
        result_args_names=('jobs',),
        flags=DbusUnprivilegedFlag,
    )
    async def enqueue_marked_jobs(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(ss)",
        result_args_names=('unit_files',),
        flags=DbusUnprivilegedFlag,
    )
    async def list_unit_files(
        self,
    ) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asas",
        result_signature="a(ss)",
        result_args_names=('unit_files',),
        flags=DbusUnprivilegedFlag,
    )
    async def list_unit_files_by_patterns(
        self,
        states: List[str],
        patterns: List[str],
    ) -> List[Tuple[str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="s",
        result_args_names=('state',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit_file_state(
        self,
        file: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asbb",
        result_signature="ba(sss)",
        result_args_names=('carries_install_info', 'changes'),
        flags=DbusUnprivilegedFlag,
    )
    async def enable_unit_files(
        self,
        files: List[str],
        runtime: bool,
        force: bool,
    ) -> Tuple[bool, List[Tuple[str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asb",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def disable_unit_files(
        self,
        files: List[str],
        runtime: bool,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ast",
        result_signature="ba(sss)",
        result_args_names=('carries_install_info', 'changes'),
        flags=DbusUnprivilegedFlag,
    )
    async def enable_unit_files_with_flags(
        self,
        files: List[str],
        flags: int,
    ) -> Tuple[bool, List[Tuple[str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ast",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def disable_unit_files_with_flags(
        self,
        files: List[str],
        flags: int,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="ast",
        result_signature="ba(sss)",
        result_args_names=('carries_install_info', 'changes'),
        flags=DbusUnprivilegedFlag,
    )
    async def disable_unit_files_with_flags_and_install_info(
        self,
        files: List[str],
        flags: int,
    ) -> Tuple[bool, List[Tuple[str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asbb",
        result_signature="ba(sss)",
        result_args_names=('carries_install_info', 'changes'),
        flags=DbusUnprivilegedFlag,
    )
    async def reenable_unit_files(
        self,
        files: List[str],
        runtime: bool,
        force: bool,
    ) -> Tuple[bool, List[Tuple[str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asbb",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def link_unit_files(
        self,
        files: List[str],
        runtime: bool,
        force: bool,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asbb",
        result_signature="ba(sss)",
        result_args_names=('carries_install_info', 'changes'),
        flags=DbusUnprivilegedFlag,
    )
    async def preset_unit_files(
        self,
        files: List[str],
        runtime: bool,
        force: bool,
    ) -> Tuple[bool, List[Tuple[str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="assbb",
        result_signature="ba(sss)",
        result_args_names=('carries_install_info', 'changes'),
        flags=DbusUnprivilegedFlag,
    )
    async def preset_unit_files_with_mode(
        self,
        files: List[str],
        mode: str,
        runtime: bool,
        force: bool,
    ) -> Tuple[bool, List[Tuple[str, str, str]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asbb",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def mask_unit_files(
        self,
        files: List[str],
        runtime: bool,
        force: bool,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asb",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def unmask_unit_files(
        self,
        files: List[str],
        runtime: bool,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="as",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def revert_unit_files(
        self,
        files: List[str],
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sb",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def set_default_target(
        self,
        name: str,
        force: bool,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
        result_args_names=('name',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_default_target(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sbb",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def preset_all_unit_files(
        self,
        mode: str,
        runtime: bool,
        force: bool,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="asssbb",
        result_signature="a(sss)",
        result_args_names=('changes',),
        flags=DbusUnprivilegedFlag,
    )
    async def add_dependency_unit_files(
        self,
        files: List[str],
        target: str,
        type: str,
        runtime: bool,
        force: bool,
    ) -> List[Tuple[str, str, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="sb",
        result_signature="as",
        result_args_names=('links',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_unit_file_links(
        self,
        name: str,
        runtime: bool,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="y",
        result_args_names=(),
        flags=DbusUnprivilegedFlag,
    )
    async def set_exit_code(
        self,
        number: int,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="u",
        result_args_names=('uid',),
        flags=DbusUnprivilegedFlag,
    )
    async def lookup_dynamic_user_by_name(
        self,
        name: str,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="u",
        result_signature="s",
        result_args_names=('name',),
        flags=DbusUnprivilegedFlag,
    )
    async def lookup_dynamic_user_by_uid(
        self,
        uid: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(us)",
        result_args_names=('users',),
        flags=DbusUnprivilegedFlag,
    )
    async def get_dynamic_users(
        self,
    ) -> List[Tuple[int, str]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="a(suuutuusu)",
        result_args_names=('entries',),
        flags=DbusUnprivilegedFlag,
    )
    async def dump_unit_file_descriptor_store(
        self,
        name: str,
    ) -> List[Tuple[str, int, int, int, int, int, int, str, int]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def version(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def features(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def virtualization(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def confidential_virtualization(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def architecture(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def tainted(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def firmware_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def firmware_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def loader_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def loader_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def kernel_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def kernel_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdtimestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdtimestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def userspace_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def userspace_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def finish_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def finish_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def security_start_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def security_start_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def security_finish_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def security_finish_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def generators_start_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def generators_start_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def generators_finish_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def generators_finish_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def units_load_start_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def units_load_start_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def units_load_finish_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def units_load_finish_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def units_load_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def units_load_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdsecurity_start_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdsecurity_start_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdsecurity_finish_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdsecurity_finish_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdgenerators_start_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdgenerators_start_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdgenerators_finish_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdgenerators_finish_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdunits_load_start_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdunits_load_start_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdunits_load_finish_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def init_rdunits_load_finish_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def log_level(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def log_target(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def nnames(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyEmitsChangeFlag,
    )
    def nfailed_units(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def njobs(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def ninstalled_jobs(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def nfailed_jobs(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def progress(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
    )
    def environment(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def confirm_spawn(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def show_status(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="as",
        flags=DbusPropertyConstFlag,
    )
    def unit_path(self) -> List[str]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def default_standard_output(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def default_standard_error(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def watchdog_device(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def watchdog_last_ping_timestamp(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def watchdog_last_ping_timestamp_monotonic(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def runtime_watchdog_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def runtime_watchdog_pre_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def runtime_watchdog_pre_governor(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def reboot_watchdog_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def kexec_watchdog_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def service_watchdogs(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def control_group(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def system_state(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="y",
    )
    def exit_code(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_timer_accuracy_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_timeout_start_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_timeout_stop_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def default_timeout_abort_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_device_timeout_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_restart_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_start_limit_interval_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
        flags=DbusPropertyConstFlag,
    )
    def default_start_limit_burst(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def default_cpuaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def default_block_ioaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def default_ioaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def default_ipaccounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def default_memory_accounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
        flags=DbusPropertyConstFlag,
    )
    def default_tasks_accounting(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_cpu(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_cpusoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_fsize(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_fsizesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_data(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_datasoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_stack(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_stacksoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_core(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_coresoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_rss(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_rsssoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_nofile(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_nofilesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_as(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_assoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_nproc(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_nprocsoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_memlock(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_memlocksoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_locks(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_lockssoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_sigpending(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_sigpendingsoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_msgqueue(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_msgqueuesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_nice(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_nicesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_rtprio(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_rtpriosoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_rttime(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def default_limit_rttimesoft(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def default_tasks_max(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def default_memory_pressure_threshold_usec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def default_memory_pressure_watch(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
        flags=DbusPropertyConstFlag,
    )
    def timer_slack_nsec(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def default_oompolicy(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
        flags=DbusPropertyConstFlag,
    )
    def default_oomscore_adjust(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
        flags=DbusPropertyConstFlag,
    )
    def ctrl_alt_del_burst_action(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="so",
        signal_args_names=('id', 'unit'),
    )
    def unit_new(self) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="so",
        signal_args_names=('id', 'unit'),
    )
    def unit_removed(self) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="uos",
        signal_args_names=('id', 'job', 'unit'),
    )
    def job_new(self) -> Tuple[int, str, str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="uoss",
        signal_args_names=('id', 'job', 'unit', 'result'),
    )
    def job_removed(self) -> Tuple[int, str, str, str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="tttttt",
        signal_args_names=('firmware', 'loader', 'kernel', 'initrd', 'userspace', 'total'),
    )
    def startup_finished(self) -> Tuple[int, int, int, int, int, int]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_args_names=(),
    )
    def unit_files_changed(self) -> None:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="b",
        signal_args_names=('active',),
    )
    def reloading(self) -> bool:
        raise NotImplementedError

