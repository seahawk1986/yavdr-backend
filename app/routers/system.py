# Module for system information (and possible operations)
from fastapi import APIRouter
from tools import systeminfo

router = APIRouter()


@router.get("/system/status")
def system_info():
    """
    Returns a json object containing system status informations:

    - **cpu_usage**: the usage per core
    - **cpu_num**: the number of cpus
    - **load_average**: the average load over the last 1, 5, 10 minutes
    - **disk_usage**: the usage of all available disks
    - **memory_usage**: memory usage infos
    - **swap_usage**: swap usage infos
    - **temperatures**: data from the temperature sensors
    - **fans**: data from the fans in the system
    - **release**: the linux distribution release
    - **kernel**: the kernel currently used
    - **system_alias**: system version information
    - **uptime**: the time the system has been running
    """
    # TODO: do this asyncronously
    return systeminfo.collect_data()
