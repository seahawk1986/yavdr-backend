#!/usr/bin/env python3
import os
import platform
import psutil


def bytes2human(n):
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%sB' % (value, s)
    return "%sB" % n

def add_human_readable(dictionary):
    keys = dictionary.keys()
    for key in list(keys):
        if isinstance(dictionary[key], int) and key != 'percent':
            dictionary[key + '_human'] = bytes2human(dictionary[key])

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
    return psutil.cpu_percent(interval=.1, percpu=True)

def load_average():
    return os.getloadavg()

def sensors_temperature():
    return psutil.sensors_temperatures()

def collect_data():
    return {
            'cpu_usage': cpu_usage(),
            'cpu_num': psutil.cpu_count(),
            'load_average': load_average(),
            'disk_usage': [p for p in disk_usage()],
            'memory_usage': memory_usage(),
            'swap_usage': swap_usage(),
            'temps': sensors_temperature(),
            'release': platform.linux_distribution(),
            'kernel': platform.release(),
            'system_alias': platform.system_alias(platform.system(), platform.release(), platform.version()),
            }

if __name__ == '__main__':
    print(collect_data())
