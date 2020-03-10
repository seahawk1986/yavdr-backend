#!/usr/bin/env python3
import datetime
import os
import platform
import subprocess
import sys
from collections import namedtuple

import distro
import psutil

from pydantic import BaseModel, constr, conlist


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return {"value": f"{value:.1f}", "unit": f"{s}B"}
    return {"value": "%s" % n, "unit": "B"}


def add_human_readable(dictionary):
    keys = dictionary.keys()
    for key in list(keys):
        if isinstance(dictionary[key], int) and key != "percent":
            dictionary[key + "_human"] = bytes2human(dictionary[key])


def disk_usage(all=False):
    def build_dict(p):
        usage = psutil.disk_usage(p.mountpoint)._asdict()
        add_human_readable(usage)
        usage.update(p._asdict())
        return usage

    partitions = psutil.disk_partitions(all=all)
    return [build_dict(p) for p in partitions]


def memory_usage():
    usage = psutil.virtual_memory()._asdict()
    add_human_readable(usage)
    return usage


def swap_usage():
    usage = psutil.swap_memory()._asdict()
    add_human_readable(usage)
    return usage


def cpu_usage():
    return psutil.cpu_percent(interval=0.1, percpu=True)


LoadAverage = namedtuple("LoadAverage", "last_min last_5_min, last_10_min")


def load_average():
    return os.getloadavg()


def sensors_temperature():
    temperature_data = {}
    for sensor_module, data in psutil.sensors_temperatures().items():
        temperature_data[sensor_module] = [s._asdict() for s in data]
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        temperature_data["nvidia_temp"] = p.stdout.strip()
    except (subprocess.CalledProcessError, IOError) as err:
        print("could not get nvidia-temperature", err, file=sys.stderr)
        pass
    return temperature_data


def sensors_fans():
    fan_data = {}
    for sensor_module, data in psutil.sensors_fans().items():
        fan_data[sensor_module] = [s._asdict() for s in data]
    return fan_data


def system_alias():
    return platform.system_alias(
        platform.system(), platform.release(), platform.version()
    )


def uptime():
    return str(
        datetime.timedelta(
            seconds=abs(
                int(datetime.datetime.utcnow().timestamp() - psutil.boot_time())
            )
        )
    )


def collect_data(include=[]):
    available_functions = {
        "cpu_usage": cpu_usage,
        "cpu_num": psutil.cpu_count,
        "load_average": load_average,
        "disk_usage": disk_usage,
        "memory_usage": memory_usage,
        "swap_usage": swap_usage,
        "temperatures": sensors_temperature,
        "fans": sensors_fans,
        "release": distro.linux_distribution,
        "kernel": platform.release,
        "system_alias": system_alias,
        "uptime": uptime,
    }
    data = {}
    for key, function in available_functions.items():
        if (include and key in include) or not include:
            data[key] = function()
    return data


if __name__ == "__main__":
    print(collect_data())
