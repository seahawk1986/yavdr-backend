import pydbus
import subprocess


def set_intel_overscan(display: str, mode: str, refresh: int, x_res: int, y_res: int):
    raise NotImplementedError("intel overscan settings not implemented")


def set_xrandr_overscan(display: str, mode: str, refresh: int, x_res: int, y_res: int):
    raise NotImplementedError("xrandr overscan settings not implemented")


def set_nvidia_overscan(
    display: str,
    mode: str,
    refresh: int,
    x_res: int,
    y_res: int,
    x_offset: int,
    y_offset: int,
):
    # nvidia-settings --assign CurrentMetaMode="DFP-0: 1280x720_50 { ViewPortIn=1280x720, ViewPortOut=1200x675+39+24}"
    cmd = [
        "nvidia-settings",
        "--assign",
        (
            "CurrentMetaMode="
            f'"{display}: {mode}_{refresh} '
            "{ "
            f"ViewPortIn={mode}, "
            f"ViewPortOut={x_res}x{y_res}+{x_offset}+{y_offset}"
            ' }"',
        ),
    ]
    try:
        subprocess.run(cmd, check=True, universal_newlines=True)
    except subprocess.CalledProcessError:
        return False
    return True
