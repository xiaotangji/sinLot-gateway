import logging
import pstats

import psutil
import simplejson


def get_cpu_percent():
    return psutil.cpu_percent()


def get_cpu_count():
    return psutil.cpu_count()


def get_memory_info():
    return psutil.virtual_memory()


def get_disk_info():
    return psutil.disk_usage('/')


def get_net_io_info():
    pass


def get_net_if_addrs():
    return psutil.net_if_addrs()


def get_net_if_stats():
    return psutil.net_if_stats()


def get_version():
    return psutil.__version__


def get_net_info():
    netcard_info = {}
    addrinfo = get_net_if_addrs()
    statinfo = get_net_if_stats()

    for k, v in addrinfo.items():
        for item in v:
            # <AddressFamily.AF_INET: 2>指IPv4的地址
            if item[0] == 2:
                netcard_info[k] = simplejson.loads(simplejson.dumps(item, ensure_ascii=False))

    for k, v in statinfo.items():
        if k in netcard_info:
            netcard_info[k].update(simplejson.loads(simplejson.dumps(v, ensure_ascii=False)))

    return netcard_info


# 获取系统启动时间
def get_boot_time():
    pass
