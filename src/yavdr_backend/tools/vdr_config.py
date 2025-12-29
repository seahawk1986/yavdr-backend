import os
import pkgconfig
from dotenv import load_dotenv

from pathlib import Path

load_dotenv()

VDR_AVAIL_DIR = Path(os.environ.get("VDR_AVAIL_DIR", "/etc/vdr/conf.avail/"))
VDR_ARGS_DIR = Path(
    os.environ.get(
        "VDR_ARGS_DIR", pkgconfig.variables("vdr").get("argsdir", "/etc/vdr/conf.d/")
    )
)
VDR_CONFIG_DIR = Path(
    os.environ.get(
        "VDR_CONFIG_DIR", pkgconfig.variables("vdr").get("configdir", "/var/lib/vdr")
    )
)