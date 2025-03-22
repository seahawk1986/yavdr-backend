import os
import pathlib
import dotenv

dotenv.load_dotenv()
# print("\n".join(f"{k}: {v}" for k, v in os.environ.items()))
VDR_CONF_DIR = pathlib.Path(os.environ.get('VDR_CONF_DIR', '/etc/vdr/'))
# print(f"{VDR_CONF_DIR=}")

async def get_VDR_CONF_DIR():
    return VDR_CONF_DIR