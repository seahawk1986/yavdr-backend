#!/usr/bin/env python3
import asyncio
import datetime
import os
import platform
import subprocess
import sys
from collections import defaultdict, deque
from typing import Dict, List, Mapping, Any, Optional, Deque

import distro
import psutil
from pydantic import BaseModel


cpu_hist = deque(maxlen=100)  # store the last 100 cpu load measurements


class HumanReadable(BaseModel):
    value: str
    unit: str


def bytes2human(n) -> HumanReadable:
    # TODO: return HumanReadable Object
    # based on http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # {"value": "9.8", "unit": "K"}
    # >>> bytes2human(100001221)
    # {"value": "95.4", "unit": "M"}
    symbols = ("K", "M", "G", "T", "P", "E", "Z", "Y")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return HumanReadable(value=f"{value:.1f}", unit=f"{s}B")
    return HumanReadable(value=f"{n}", unit="B")


def add_human_readable(dictionary) -> None:
    keys = dictionary.keys()
    for key in list(keys):
        if isinstance(dictionary[key], int) and key != "percent":
            dictionary[key + "_human"] = bytes2human(dictionary[key])


class DiskUsageValues(BaseModel):
    total: float
    used: float
    free: float
    percent: float
    total_human: HumanReadable
    used_human: HumanReadable
    free_human: HumanReadable
    device: str
    mountpoint: str
    fstype: str
    opts: str


def disk_usage(all=False) -> List[DiskUsageValues]:
    def build_dict(p):
        usage = psutil.disk_usage(p.mountpoint)._asdict()
        add_human_readable(usage)
        usage.update(p._asdict())
        return usage

    partitions = psutil.disk_partitions(all=False)
    return [build_dict(p) for p in partitions if not p.device.startswith("/dev/loop")]


class MemoryUsage(BaseModel):
    total: float
    available: float
    percent: float
    used: float
    free: float
    active: float
    inactive: float
    buffers: float
    cached: float
    shared: float
    slab: float
    total_human: HumanReadable
    available_human: HumanReadable
    used_human: HumanReadable
    free_human: HumanReadable
    active_human: HumanReadable
    inactive_human: HumanReadable
    buffers_human: HumanReadable
    cached_human: HumanReadable
    shared_human: HumanReadable
    slab_human: HumanReadable


def memory_usage() -> Mapping[str, Any]:
    usage = psutil.virtual_memory()._asdict()
    add_human_readable(usage)
    return usage


class SwapUsage(BaseModel):
    total: float
    used: float
    free: float
    percent: float
    sin: float
    sout: float
    total_human: HumanReadable
    used_human: HumanReadable
    free_human: HumanReadable
    sin_human: HumanReadable
    sout_human: HumanReadable


def swap_usage() -> Mapping[str, float]:
    usage = psutil.swap_memory()._asdict()
    add_human_readable(usage)
    return usage


class LoadAverage(BaseModel):
    last_min: float
    last_5_min: float
    last_10_min: float


def load_average() -> LoadAverage:
    last_min, last_5_min, last_10_min = (
        os.getloadavg()
    )  # only newer versions of psutil wrap this call
    return LoadAverage(
        last_min=last_min, last_5_min=last_5_min, last_10_min=last_10_min
    )


class TempValue(BaseModel):
    label: str
    current: Optional[float]
    high: Optional[float]
    critical: Optional[float]


class Temperatures(BaseModel):
    sensors: Dict[str, List[TempValue]]


def sensors_temperature() -> Temperatures:
    temperature_data = defaultdict(list)
    try:
        p = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            check=True,
        )
        nvidia_temp = p.stdout.strip()
        if nvidia_temp:
            temperature_data["nvidia"] = [
                {
                    "label": "GPU",
                    "current": float(p.stdout.strip()),
                    "critical": 115,
                    "high": 80,
                }
            ]
    except (subprocess.CalledProcessError, IOError) as err:
        print("could not get nvidia-temperature", err, file=sys.stderr)
        pass
    for sensor_module, data in psutil.sensors_temperatures().items():
        sensors_seen = set()
        for sensor in data:
            if sensor.label not in sensors_seen:
                temperature_data[sensor_module].append(sensor._asdict())
                sensors_seen.add(sensor.label)

    return Temperatures(sensors=temperature_data)


class Fan(BaseModel):
    label: Optional[str]
    current: Optional[float]


class Fans(BaseModel):
    sensors: Mapping[str, List[Fan]]


def sensors_fans() -> Fans:
    fan_data = {}
    for sensor_module, data in psutil.sensors_fans().items():
        fan_data[sensor_module] = [s._asdict() for s in data]
    # print(fan_data)
    return Fans(sensors=fan_data)


def system_alias() -> List[str]:
    return platform.system_alias(
        platform.system(), platform.release(), platform.version()
    )


def uptime() -> str:
    return str(
        datetime.timedelta(
            seconds=abs(
                int(datetime.datetime.utcnow().timestamp() - psutil.boot_time())
            )
        )
    )


class SystemData(BaseModel):
    cpu_usage: List[float]
    cpu_num: int
    # cpu_hist: List[Tuple[float, ...]]
    load_average: LoadAverage
    disk_usage: List[DiskUsageValues]
    memory_usage: MemoryUsage
    swap_usage: SwapUsage
    temperatures: Temperatures
    fans: Fans
    release: List[str]
    kernel: str
    system_alias: List[str]
    uptime: str


def cpu_usage() -> List[float]:
    # return CpuUsage.parse_obj(psutil.cpu_percent(interval=0.1, percpu=True))
    cpu_load = psutil.cpu_percent(percpu=True)
    return cpu_load


def collect_data(include=[]) -> SystemData:
    available_functions = {
        "cpu_usage": cpu_usage,
        "cpu_num": psutil.cpu_count,
        # "cpu_hist": get_cpu_hist,
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
    return SystemData(**data)


class SystemStatHistory():
    # TODO: collect system data continously, so clients can request data without delay
    #       and the number of requests does not influence the number of data points
    def __init__(self, hist_len=100) -> None:
        self.cpu_hist: Deque[List[float]] = deque(maxlen=hist_len)
        self.mem_hist: Deque[float] = deque(maxlen=hist_len)
        self.fan_hist: Deque[Mapping[str, Fans]] = deque(maxlen=hist_len)
        self.current_cpu_data = cpu_usage()
        self.current_memory_data = memory_usage()
        self.current_swap_data = swap_usage()

    async def run_update(self):
        while True:
            await asyncio.sleep(.5)
            self.update_cpu_hist()
            self.update_ram_hist()
            self.update_fan_hist()

    def update_cpu_hist(self) -> None:
        cpu_load = psutil.cpu_percent(percpu=True)
        self.cpu_hist.append(cpu_load)

    def update_ram_hist(self) -> None:
        data = memory_usage()
        self.mem_hist.append(data["percent"])

    def update_fan_hist(self) -> None:
        data = sensors_fans()
        self.mem_hist.append(data)

    @property
    def cpu_history_per_core(self) -> List[List[float]]:
        return list(map(list, zip(*self.cpu_hist)))

    def collect_data(self) -> SystemData:
        self.cpu_history_per_core
        pass


if __name__ == "__main__":
    print(collect_data())
