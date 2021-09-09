import json
import logging

from aiohttp import web
import simplejson

from thingsboard_gateway.db_access.ethernet_dao import EthernetDao
from thingsboard_gateway.db_access.slave_ip_dao import SlaveIpDao
from thingsboard_gateway.network import net_interface
from thingsboard_gateway.web import web_error_code
from thingsboard_gateway.web.web_common import WebCommon

log = logging.getLogger('service')
ethernetDao = EthernetDao()
slaveIpDao = SlaveIpDao()


def check_db_connect():
    if not ethernetDao.init_success:
        ethernetDao.re_init()
    if not slaveIpDao.init_success:
        slaveIpDao.re_init()


async def getEthernetInfo(request):
    net_info = net_interface.get_net_info()

    return web.Response(content_type='application/json', body=simplejson.dumps(net_info, ensure_ascii=False),
                        charset="utf-8")


# 系统信息
async def getSystemInfo(request):
    map = {}
    system_info = ""
    try:
        memory_percent = net_interface.get_memory_info().percent
        memory_userd = int(net_interface.get_memory_info().used/1024/1024)
        memory_total = int(net_interface.get_memory_info().total/1024/1024)
        memory_used_total = str(memory_userd)+'/'+str(memory_total)
        net = net_interface.get_net_info()
        netmask = net['wlan0']['netmask']
        ip = net['wlan0']['address']
        isup = net['wlan0']['isup']
        mtu = net['wlan0']['mtu']
        cpu_percent = net_interface.get_cpu_percent()
        cpu_count = net_interface.get_cpu_count()
        version = net_interface.get_version()
        status = net_interface.get_net_if_stats()
        netAddr = net_interface.get_net_if_addrs()
        disk = net_interface.get_disk_info()
        map['cpuPercent'] = cpu_percent
        map['memory_percent'] = memory_percent
        map['memory_used_total'] = memory_used_total
        map['ip'] = ip
        map['disk'] = disk
        map['version'] = version
        map['cpuCount'] = cpu_count
        map['netmask'] = netmask
        map['isup'] = isup
        map['mtu'] = mtu
        system_info = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on getCpuInfo:")
        log.exception(e)
        system_info = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=system_info, charset="utf-8")


async def selectFromEthernetByName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        name = data.get('data').get('name')
        lst = ethernetDao.get_one(name)
        rt_json = WebCommon.getNormalJson(lst, web_error_code.FAILED)
    except Exception as e:
        log.error("Error on selectFromEthernetByName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(-1, web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 添加以太网
async def addEthernet(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        ethernet = data.get('data')
        rt = ethernetDao.insertEthernet(ethernet)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addEthernet:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(-1, web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 根据以太网名称修改
async def updateEthernetByName(request):
    rt_json = ""
    try:
        data = await request.json()
        ethernet = data.get('data')
        ethernetInfo = selectFromEthernetByName(request)
        if ethernetInfo is not None:
            rt = ethernetDao.update(ethernet)
        else:
            addEthernet(request)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 查询所有从ip
async def selectFromSlaveIpConfig(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        lst = slaveIpDao.get_all()
        rt_json = WebCommon.getNormalJson(lst, web_error_code.FAILED)
    except Exception as e:
        log.error("Error on selectFromSlaveIpConfig:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(-1, web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 添加从ip
async def addSlaveIp(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        slave = data.get('data')
        rt = slaveIpDao.insertSlave(slave)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addDevice:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(-1, web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 根据id修改
async def updateSlaveIpById(request):
    rt_json = ""
    try:
        data = await request.json()
        ethernet = data.get('data')
        rt = ethernetDao.update(ethernet)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 删除从ip信息
async def deleteSlaveById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        id = data.get('data')
        slaveIpDao.deleteSlave(id.get('id'))
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")
