from collections import defaultdict, deque
import re
import subprocess
from pathlib import Path
import sys

from pydantic import BaseModel

from .vdr_config import VDR_AVAIL_DIR, VDR_ARGS_DIR
from yavdr_backend.models.vdr_start_arguments import PluginConfig, ArgumentFile


RE_SECTION = re.compile(r"^\s*\[(?P<sectionname>[^]]+)\]\s*$", re.MULTILINE)

# Given the way the VDR parses the ARGDIR there are the following rules:
# the section [vdr] can occur multiple times, all arguments are appended to a list
# each occurence of any other section will cause a new --plugin={section} to be added,
# so you can't split plugin arguments over multiple files under the same section name
# This creates a problem: in theory there might be multiple sections in a file, so
# removing the symlink from the AVAILDIR to the ARGSDIR will could affect multiple plugins and the VDR.
#



def parse_argument_file(path: Path, help_collection: dict[str, str]) -> tuple[list[str], ArgumentFile]:
    prio = 50
    PRIO_PLUGIN = re.compile(r"^((?P<prio>\d+)\-)?(?P<name>.+)\.conf$")
    content = path.read_text()
    sections = RE_SECTION.findall(content)
    try:
        first_section = sections[0]
    except IndexError:
        first_section = ''

    if m := PRIO_PLUGIN.match(str(path.name)):
        g = m.groupdict()
        name = g['name']
        priostr = g.get("prio")
        if not priostr:
            priostr = 99 if name == 'dynamite' else 50
        prio = int(priostr)
        return sections, ArgumentFile(
            filename=path,
            name=name,
            prio=prio,
            enabled=(path.parent == VDR_ARGS_DIR),
            static=(path.resolve().parent == VDR_ARGS_DIR),
            args=content,
            help=help_collection.get(first_section, ''),
            warning="multiple sections" if len(sections) > 1 else ("no sections" if not sections else None),
        )
    else:
        print(f"{content=}")

        raise ValueError(f"invalid config file {path}")


def process_argument_file(
    filename: Path, configs: defaultdict[str, list[ArgumentFile]], help_collection: dict[str, str]
):
    sections, config = parse_argument_file(filename, help_collection)

    try:
        config_for, *_ = (s for s in sections if s != "header")
    except ValueError:
        config_for = config.name

    configs[config_for].append(config)
    # print(f"processed {filename}")
    for k, v in configs.items():
        configs[k] = sorted(v, key=lambda x: x.filename.name)
    return configs


def read_vdr_arguments() -> defaultdict[str, list[ArgumentFile]]:
    # config_dict: dict[str, ArgumentFile] = dict()
    enabled_configs: set[Path] = set()
    available_configs: set[Path] = set()

    configs: defaultdict[str, list[ArgumentFile]] = defaultdict(list)
    configs['vdr'] = []
    help_collection = read_vdr_help()

    for f in sorted(VDR_ARGS_DIR.glob("*.conf")):
        if not f.is_file():
            continue
        static = not f.is_symlink()
        if not static:
            print(f"symlink: {f}")
            abs_path = f.resolve()
            if abs_path.exists():
                enabled_configs.add(f.resolve())
                configs = process_argument_file(f, configs, help_collection)
            else:
                print("Warning, {abs_path} does not exist, skipping")
        else:
            print(f"static file: {f}")
            configs = process_argument_file(f, configs, help_collection)


    for f in sorted(VDR_AVAIL_DIR.glob("*.conf")):
        if not f.is_file() or f in enabled_configs:
            continue
        configs = process_argument_file(f, configs, help_collection)
        available_configs.add(f)

    # disabled_configs: set[Path] = available_configs - enabled_configs

    return configs


def read_vdr_help(plugin_name: str | None = None) -> dict[str, str]:
    args = ["vdr", "--help"]
    if plugin_name:
        args.append(f"-P{plugin_name}")
    output = subprocess.check_output(args, universal_newlines=True)
    vdr_help, _, plugin_help_text = output.partition(
        'Plugins: vdr -P"name [OPTIONS]"\n\n'
    )

    if plugin_name and plugin_help_text.startswith(plugin_name):
        return {plugin_name: plugin_help_text}

    help_collection: dict[str, str] = {
        "vdr": vdr_help,
    }

    help_data: defaultdict[str, list[str]] = defaultdict(list)
    current_plugin = None
    for line in plugin_help_text.splitlines():
        if line and not line[0].isspace():
            current_plugin, _, _ = line.partition(" ")
        if current_plugin:
            help_data[current_plugin].append(line)
    for name, plugin_description in help_data.items():
        help_collection[name] = "\n".join(plugin_description)

    return help_collection


async def write_argument_file(config: PluginConfig) -> bool:
    # print(f"writing config for: {config.name}, {VDR_ARGS_DIR=}")
    ARGS_PRIO_RE = re.compile(rf"^((?P<prio>\d+)\-){config.name}\.conf$")
    # print(f"{list(VDR_ARGS_DIR.glob(f'*-{config.name}.conf'))=}")
    enabled_config_files = set(VDR_ARGS_DIR.glob(f'*-{config.name}.conf'))
    linked_files = {c for c in enabled_config_files if c.is_symlink()}
    # print(f"{enabled_config_files=}, {linked_files=}")
    static_files = enabled_config_files - linked_files
    prio = config.prio if config.prio else 50
    # look for the config file
    # print(f"config file name is {(VDR_AVAIL_DIR / f'{config.name}.conf').is_file()}")
    if (avail_file := VDR_AVAIL_DIR / f'{config.name}.conf').is_file():
        print(f"{avail_file=}")
        avail_file.write_text(config.arguments)
        cfg_linked_files: list[Path] = []
        cfg_prios: set[int] = set()
        for cfg in linked_files:
            print(f"{cfg.resolve() == avail_file=}")
            if cfg.resolve() == avail_file:
                cfg_linked_files.append(cfg)
                if (m := ARGS_PRIO_RE.match(cfg.name)):
                    cfg_prios.add(int(prio :=m.groupdict()['prio']) if m else 50)

        if not config.enabled or config.prio:
            deque(map(lambda x: x.unlink(), cfg_linked_files), maxlen=0) # consume the map
        if (
            (config.enabled and config.prio) or
            not cfg_linked_files # it's a non-static file that is currently not linked to the VDR_CONF_DIR
        ):
            (VDR_ARGS_DIR / f"{prio}-{config.name}.conf").symlink_to(avail_file)

    else:
        # this is a static file - no prio changes, not symlinks
        candidates = [p for p in static_files if (m := ARGS_PRIO_RE.match(p.name))]
        if not candidates:
            print("no matching file found", file=sys.stderr)
            raise ValueError(f"no matching file found for {config.name}")
        if len(candidates) > 1:
            print(f"warning: more than one candidate found: {candidates}", file=sys.stderr)
            return False

        cfg_file = candidates[0]
        cfg_file.write_text(config.arguments)
    return True


if __name__ == "__main__":
    args = read_vdr_arguments()
    for name, arglist in args.items():
        if name == "vdr":
            print(name)
            for arg in arglist:
                print(arg)
