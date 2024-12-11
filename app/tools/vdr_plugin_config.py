import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Generator, Iterable, List, Mapping, Tuple

from pydantic import BaseModel, Extra  # , constr, conlist


VDR_CONFIG_DIR = Path("/etc/vdr/conf.avail/")
VDR_ARGS_DIR = Path("/etc/vdr/conf.d/")
RE_SECTION = re.compile(r"^\[(?P<plugin_name>[a-zA-Z-]*)\]")


class PluginConfig(BaseModel):
    name: str
    enabled: bool
    prio: int
    arguments: str = ""
    help: str = ""

    class Config:
        extra = "ignore"

    # def __init__(self, name, enabled, prio=None, arguments=list(), help="", *args, **kwargs):
    #     prio = prio if prio is not None else (50 if name != "dynamite" else 99)
    #     help_data = read_plugin_help(name)
    #     help = []
    #     if help_data:
    #         help = help_data.get(name) or []
    #     super().__init__(
    #         name=name,
    #         enabled=enabled,
    #         prio=prio,
    #         arguments=arguments,
    #         help=help,
    #     )


def parse_config_file(path: Path) -> Mapping[str, List[str]]:
    # TODO: do we need to keep comment lines?
    data = defaultdict(list)
    on_plugin_config = False
    plugin_name = None
    for line in path.read_text().splitlines():
        line = line.strip()
        if not on_plugin_config and (
            not line or line.startswith("#")
        ):  # skip comments before the actual config
            continue

        # check for sections
        if m := re.match(RE_SECTION, line):
            plugin_name, *_ = m.groups()
            on_plugin_config = True
        elif on_plugin_config:
            data[plugin_name].append(line)
    return data


def write_config_file(path: Path, data: List[str]) -> bool:
    """write configuration file"""
    # TODO: validate data, at least one leading "[NAME]" element is required before emtpy and non-comment lines
    try:
        with open(path, "w") as f:
            f.writelines(data)
    except IOError as err:
        print(f"writing config to {path=} failed: {err}")
        return False
    else:
        return True


def extract_name_prio(plugin_links: Iterable[Path]) -> Generator[Tuple[str, int], Any, Any]:
    for p in plugin_links:
        prio, _, name = p.stem.partition("-")
        # in case there is no priority
        if not prio.isdecimal or not name:
            name = prio
            prio = 50
        # print(p, prio, name)
        yield name, int(prio)


def read_plugin_help(plugin_name: str | None = None) -> dict[str, str]:
    args = ["vdr"]
    if plugin_name is not None:
        args.append(f"-P{plugin_name}")
    args.append("-h")
    _, _, help_text = subprocess.run(
        args, capture_output=True, text=True
    ).stdout.partition('Plugins: vdr -P"name [OPTIONS]"\n\n')
    if plugin_name and help_text.startswith(plugin_name):
        return {plugin_name: help_text}
    else:
        help_data = defaultdict(list)
        help_str: dict[str, str] = dict()
        current_plugin = None
        for line in help_text.splitlines():
            if line and not line[0].isspace():
                current_plugin, _, _ = line.partition(" ")
            help_data[current_plugin].append(line)
        for p, v in help_data.items():
            help_str[p] = "\n".join(v)
        return help_str


def read_plugins() -> dict[str, PluginConfig]:
    help_data = read_plugin_help()  # read the help output produced by vdr

    available_configuration_files = set(VDR_CONFIG_DIR.glob("*.conf"))
    active_configuration_files = set(VDR_ARGS_DIR.glob("*.conf"))

    static_configuration_files = set(
        p for p in active_configuration_files if not p.is_symlink()
    )
    linked_configuration_files = active_configuration_files - static_configuration_files
    disabled_configuration_files = (
        available_configuration_files - linked_configuration_files
    )

    configuration_files = {}
    cfg_priorities = {
        name: priority
        for name, priority in extract_name_prio(linked_configuration_files)
    }

    # TODO: move to a file-based output instead of wildly combining data

    available_plugins = set(VDR_CONFIG_DIR.glob("*.conf"))
    enabled_plugins_symlinks = [
        p
        for p in VDR_ARGS_DIR.glob("*.conf")
        if p.is_symlink() and p.resolve().parent == VDR_CONFIG_DIR
    ]
    priorities = {
        name: priority for name, priority in extract_name_prio(enabled_plugins_symlinks)
    }
    enabled_plugins = set(p.resolve() for p in enabled_plugins_symlinks)
    disabled_plugins = available_plugins - enabled_plugins

    plugins = {}

    for p in enabled_plugins:
        d = parse_config_file(p)
        if len(d) == 0:
            d = dict([(p.stem, [])])
        elif len(d) > 1:
            # more than one plugin configured in the file
            print("we got options for more than one plugin in the configuration file")
        for plugin_name, arguments in d.items():
            if plugin_name not in plugins:
                prio = priorities.get(plugin_name)
                prio = (
                    prio
                    if prio is not None
                    else (50 if plugin_name != "dynamite" else 99)
                )
                plugins[plugin_name] = PluginConfig(
                    name=plugin_name,
                    enabled=True,
                    prio=prio,
                    arguments="\n".join(arguments),
                    help=help_data.get(plugin_name, ""),
                )
            elif arguments:
                print(f"add arguments {arguments}")
                plugins[plugin_name].arguments.extend(arguments)

    for p in disabled_plugins:
        d = parse_config_file(p)
        if len(d) > 1:
            # more than one plugin configured in the file
            print("we got options for more than one plugin in the configuration file")
        for plugin_name, arguments in d.items():
            if plugin_name not in plugins:
                prio = 50 if plugin_name != "dynamite" else 99
                plugins[plugin_name] = PluginConfig(
                    name=plugin_name,
                    enabled=False,
                    prio=prio,
                    arguments="\n".join(arguments),
                    help=help_data.get(plugin_name, ""),
                )
            else:
                plugins[plugin_name].arguments.extend(arguments)

    return plugins


if __name__ == "__main__":
    for p_name, p in sorted(read_plugins().items()):
        print(p_name, p.help)
