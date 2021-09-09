import asyncio
import datetime
import json
import time

import simplejson
import logging

from aiohttp import web

from thingsboard_gateway.db_access.access_control_list_dao import AccessControlListDao
from thingsboard_gateway.db_access.access_control_strategy_dao import AccessControlStrategyDao
from thingsboard_gateway.db_access.connector_dao import ConnectorDao
from thingsboard_gateway.db_access.device_dao import DeviceDao
from thingsboard_gateway.db_access.device_variable_dao import DeviceVariableDao
from thingsboard_gateway.db_access.dhcp_dao import DhcpDao
from thingsboard_gateway.db_access.monitor_dao import MonitorDao
from thingsboard_gateway.db_access.routing_static_dao import RoutingStaticDao
from thingsboard_gateway.db_access.ssid_dao import SsidDao
from thingsboard_gateway.db_access.static_ip_config_dao import StaticIpConfigDao
from thingsboard_gateway.db_access.system_dao import SystemDao
from thingsboard_gateway.db_access.topic_dao import TopicDao
from thingsboard_gateway.db_access.user_dao import UserDao
from thingsboard_gateway.db_access.wlan_dao import WlanDao
from thingsboard_gateway.web import web_error_code
from thingsboard_gateway.web.web_common import WebCommon
from thingsboard_gateway.gateway.tb_gateway_service import TBGatewayService

log = logging.getLogger('service')

connectDao = ConnectorDao()
deviceDao = DeviceDao()
deviceVariableDao = DeviceVariableDao()
topicDao = TopicDao()
monitorDao = MonitorDao()
systemDao = SystemDao()
wlanDao = WlanDao()
ssidDao = SsidDao()
dhcpDao = DhcpDao()
staticIpConfigDao = StaticIpConfigDao()
routingStaticDao = RoutingStaticDao()
accessControlStrategyDao = AccessControlStrategyDao()
accessControlListDao = AccessControlListDao()
tbgateway_service = TBGatewayService()
userDao = UserDao()


def check_db_connect():
    if not connectDao.init_success:
        connectDao.re_init()
    if not deviceDao.init_success:
        deviceDao.re_init()
    if not deviceVariableDao.init_success:
        deviceVariableDao.re_init()
    if not topicDao.init_success:
        topicDao.re_init()
    if not monitorDao.init_success:
        monitorDao.re_init()
    if not systemDao.init_success:
        systemDao.re_init()
    if not wlanDao.init_success:
        wlanDao.re_init()
    if not ssidDao.init_success:
        ssidDao.re_init()
    if not dhcpDao.init_success:
        dhcpDao.re_init()
    if not staticIpConfigDao.init_success:
        staticIpConfigDao.re_init()
    if not routingStaticDao.init_success:
        routingStaticDao.re_init()
    if not accessControlStrategyDao.init_success:
        accessControlStrategyDao.re_init()
    if not accessControlListDao.init_success:
        accessControlListDao.re_init()
    if not userDao.init_success:
        userDao.re_init()


async def startConnector(request):
    pass


async def stopConnector(request):
    pass


async def updateDeviceVariable(request):
    data = await request.post()


async def updateDeviceParameter(request):
    pass


# 分页查询设备
async def selectAllFromDevice(request):
    rt_json = ""
    map = {}
    id_ConTypeMap = {}
    conName_IdMap = {}
    conNameList = []
    deviceNameList = []
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        deviceName = data.get('deviceName')
        sqlStartIndex = int(data.get('sqlStartIndex'))
        sqlNumber = int(data.get('sqlNumber'))
        sortField = data.get('sortField')
        sortType = data.get('sortType')
        count = deviceDao.get_count_by_name(deviceName)
        all = connectDao.get_all()
        for con in all:
            conNameList.append(con.get('name'))
            if con.get('id') not in id_ConTypeMap:
                id_ConTypeMap[con.get('id')] = con.get('protocol_type')
            conName_IdMap[con.get('name')] = con.get('id')
        listDevice = deviceDao.selectAllFromDevice(deviceName, sqlStartIndex, sqlNumber, sortField, sortType)
        deviceList = deviceDao.get_device_name_all_list()
        for devName in deviceList:
            deviceNameList.append(devName['device_name'])
        for dev in listDevice:
            if dev['device_status'] == 1:
                dev['deviceStatus'] = '在线'
            else:
                dev['deviceStatus'] = '离线'
            if dev.get('connector_type') in id_ConTypeMap:
                dev['con_type'] = id_ConTypeMap[dev.get('connector_type')]
            if dev['ip_enable'] == 1:
                dev['ipEnable'] = '是'
            else:
                dev['ipEnable'] = '否'
        map['conName'] = conNameList
        map['data'] = listDevice
        map["idProtocol"] = id_ConTypeMap
        map["conNameId"] = conName_IdMap
        map['count'] = count
        map['deviceName'] = deviceNameList
        rt_json = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectAllFromCon:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 添加设备
async def addDevice(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        device = data.get('data')
        device_name = device.get('device')['device_name']
        connector_name = device.get('device')['connector_name']

        lst = deviceDao.get_one(device_name)
        if len(lst) > 0:
            rt_json = WebCommon.getNormalJson(1, web_error_code.FAILED)
        else:
            connect_type = connectDao.selectIdFromConByConName(connector_name)
            device.get('device')['connector_type'] = connect_type
            rt = deviceDao.insertDev(device)
            if rt > 0:
                tbgateway_service.reload_device_variable(connector_name, device_name)
            rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addDevice:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(-1, web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 删除设备
async def deleteDeviceByDeviceName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        device_name = data.get('data')
        connect_name = deviceDao.get_connector_name(device_name['deviceName'])
        deviceDao.delete(device_name['deviceName'])
        tbgateway_service.remove_device(connect_name, device_name['deviceName'])
        deviceVariableDao.deleteName(device_name['deviceName'])
        count = deviceDao.get_count()
        rt_json = WebCommon.getNormalJson(count, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 根据设备名称修改
async def updateDeviceByDeviceName(request):
    rt_json = ""
    try:
        data = await request.json()
        device = data.get('data')
        rt = deviceDao.update(device['device'])
        if rt > 0:
            connect_name = deviceDao.get_connector_name(device['device']['device_name'])
            tbgateway_service.reload_device_variable(connect_name, device['device']['device_name'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 根据设备名称修改
async def updateRequestByDeviceName(request):
    rt_json = ""
    try:
        data = await request.json()
        device = data.get('data')
        device['device']['con_request'] = str(device['device']['con_request'])
        device['device']['discon_request'] = str(device['device']['discon_request'])
        rt = deviceDao.updateRequest(device['device'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")

# 分页查询连接器信息
async def selectAllFromCon(request):
    rt_json = ""
    map = {}
    conNameList = []
    conTypeList = set()
    selfTypeList = set()
    selfTypeArr = []
    conTypeArr = []
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        conName = data.get('conName')
        sqlStartIndex = int(data.get('sqlStartIndex'))
        sqlNumber = int(data.get('sqlNumber'))
        sortField = data.get('sortField')
        sortType = data.get('sortType')

        listcon = connectDao.selectAllFromCon(conName, sqlStartIndex, sqlNumber, sortField, sortType)
        count = connectDao.get_count_by_name(conName)
        all = connectDao.get_all()

        for con in all:
            conNameList.append(con.get('name'))
            conTypeList.add(con.get('protocol_type'))
            selfTypeList.add(con.get('self_type'))
        for res in selfTypeList:
            selfTypeArr.append(res)

        for res in conTypeList:
            conTypeArr.append(res)

        map['conName'] = conNameList
        map['conType'] = conTypeArr
        map['selfType'] = selfTypeArr
        map['data'] = listcon
        map['count'] = count

        rt_json = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectAllFromCon:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteConByconName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        con = data.get('data')
        connectDao.delete(con['conName'])
        tbgateway_service.remove_connector(con['conName'])
        count = connectDao.get_countFromCon()
        rt_json = WebCommon.getNormalJson(count, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 添加连接器
async def addCon(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        connect_type = connectDao.selectIdFromConByConName(data.get('connector').get('name'))
        if connect_type is None:
            rt = connectDao.insertCon(data)
            rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
            # add connect to config
            # tbgateway_service.add_connector(data.get('connector'))
    except Exception as e:
        log.error("Error on addCon:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 根据连接器名称修改连接器
async def updateConByName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        con = data.get('connector')
        if con.get('name'):
            rt = connectDao.update(con)
            if rt > 0:
                tbgateway_service.update_connector(data.get('connector'))
            rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def selectAllFromDeviceVariable(request):
    rt_json = ""
    map = {}
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        id = data.get('id')
        if id is None:
            rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED)
            return web.Response(content_type='application/json', body=rt_json, charset="utf-8")
        sqlStartIndex = int(data.get('sqlStartIndex'))
        sqlNumber = int(data.get('sqlNumber'))
        sortField = data.get('sortField')
        sortType = data.get('sortType')
        count = deviceVariableDao.get_count_by_devId(id)
        listDeviceV = deviceVariableDao.selectAllFromDeviceVariable(id, sqlStartIndex, sqlNumber, sortField, sortType)
        map['data'] = listDeviceV
        map['count'] = count
        rt_json = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectAllFromDeviceVariable:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def selectJsonFromDeviceByDeviceName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        deviceName = data.get('deviceName')
        jsons = deviceDao.selectJsonFromDeviceByDeviceName(deviceName)
        if jsons is not None:
            rt_json = WebCommon.getNormalJson(jsons[0]['json'], web_error_code.SUCCESS)
        else:
            rt_json = WebCommon.getNormalFalseJson(web_error_code.SUCCESS)

    except Exception as e:
        log.error("Error on selectJsonFromDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addDeviceVariable(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')['deviceVariable']
        iddev = deviceDao.selectDeviceIdByDeviceName(data['device_name'])
        data['device_id'] = iddev[0]['id']
        rt = deviceVariableDao.insertDevVariable(json.dumps(data))
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
        # TBD
    except Exception as e:
        log.error("Error on addDeviceVariable:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteDeviceVariableById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        devVariable = data.get('data')
        deviceid = deviceVariableDao.get_device_id(devVariable['id'])
        device = deviceDao.get_one_by_id(deviceid)
        deviceVariableDao.delete(devVariable['id'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteDeviceVariableById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateDeviceVariableById(request):
    rt_json = ""
    try:
        data = await request.json()
        devVariable = data.get('data')['deviceVariable']
        deviceId = deviceVariableDao.get_device_id(devVariable['id'])
        device = deviceDao.get_one_by_id(deviceId)
        rt = deviceVariableDao.update(devVariable)
        if rt > 0:
            tbgateway_service.reload_device_variable(device["connector_name"], device['device_name'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateDeviceVariableById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def selectAllFromTopic(request):
    rt_json = ""
    map = {}
    topicFilter = []
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        sqlStartIndex = int(data.get('sqlStartIndex'))
        sqlNumber = int(data.get('sqlNumber'))
        sortField = data.get('sortField')
        sortType = data.get('sortType')
        topiclist = topicDao.selectAllFromTopic(sqlStartIndex, sqlNumber, sortField, sortType)
        for t in topiclist:
            topicFilter.append(t['topicFilter'])
        map['data'] = topiclist
        map['count'] = len(topiclist)
        map['topicList'] = topicFilter
        rt_json = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectAllFromTopic:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addTopic(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        rt = topicDao.insertTopic(data)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addTopic:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromTopicByTopicName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        topic = data.get('data')
        topicDao.delete(topic['topicName'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromTopicByTopicName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateTopicByTopicName(request):
    rt_json = ""
    try:
        data = await request.json()
        topic = data.get('data')['topic']
        rt = topicDao.update(topic)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateTopicByTopicName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def selectJsonUpdateJsonRpcJsonFromDeviceByDeviceName(request):
    rt_json = ""
    try:
        data = await request.json()
        check_db_connect()
        data = data.get('data')
        devicename = data.get('deviceName')
        jsonlist = deviceDao.selectJsonUpdateJsonRpcJsonFromDeviceByDeviceName(devicename)
        rt_json = WebCommon.getNormalJson(jsonlist, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectJsonUpdateJsonRpcJsonFromDeviceByDeviceName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateMonitorSetting(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        monitor = data.get('data')['monitorSetting']
        rt = monitorDao.update(monitor)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateMonitorSetting:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def selectFromMonitor(request):
    rt_json = ""
    try:
        check_db_connect()
        monitor = monitorDao.selectFromMonitor()
        rt_json = WebCommon.getNormalJson(monitor, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromMonitor:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


def getDayMonitor(listday=[]):
    mapday = {}
    for day in listday:
        date = str(day['record_time']).split(" ")[0]
        record = str(day['record_time'])
        if compareTime(record, date + ' 00:00:00') >= 0 and compareTime(record, date + ' 00:00:59') <= 0:
            col = mapday.get(date + ' 00:00:00')
            if col is None:
                mapday[date + ' 00:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 01:00:00') >= 0 and compareTime(record, date + ' 01:00:59') <= 0:
            col = mapday.get(date + ' 01:00:00')
            if col is None:
                mapday[date + ' 01:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 02:00:00') >= 0 and compareTime(record, date + ' 02:00:59') <= 0:
            col = mapday.get(date + ' 02:00:00')
            if col is None:
                mapday[date + ' 02:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 03:00:00') >= 0 and compareTime(record, date + ' 03:00:59') <= 0:
            col = mapday.get(date + ' 03:00:00')
            if col is None:
                mapday[date + ' 03:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 04:00:00') >= 0 and compareTime(record, date + ' 04:00:59') <= 0:
            col = mapday.get(date + ' 04:00:00')
            if col is None:
                mapday[date + ' 04:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 05:00:00') >= 0 and compareTime(record, date + ' 05:00:59') <= 0:
            col = mapday.get(date + ' 05:00:00')
            if col is None:
                mapday[date + ' 05:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 06:00:00') >= 0 and compareTime(record, date + ' 06:00:59') <= 0:
            col = mapday.get(date + ' 06:00:00')
            if col is None:
                mapday[date + ' 06:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 07:00:00') >= 0 and compareTime(record, date + ' 07:00:59') <= 0:
            col = mapday.get(date + ' 07:00:00')
            if col is None:
                mapday[date + ' 07:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 08:00:00') >= 0 and compareTime(record, date + ' 08:00:59') <= 0:
            col = mapday.get(date + ' 08:00:00')
            if col is None:
                mapday[date + ' 08:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 09:00:00') >= 0 and compareTime(record, date + ' 09:00:59') <= 0:
            col = mapday.get(date + ' 09:00:00')
            if col is None:
                mapday[date + ' 09:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 10:00:00') >= 0 and compareTime(record, date + ' 10:00:59') <= 0:
            col = mapday.get(date + ' 10:00:00')
            if col is None:
                mapday[date + ' 10:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 11:00:00') >= 0 and compareTime(record, date + ' 11:00:59') <= 0:
            col = mapday.get(date + ' 11:00:00')
            if col is None:
                mapday[date + ' 11:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 12:00:00') >= 0 and compareTime(record, date + ' 12:00:59') <= 0:
            col = mapday.get(date + ' 12:00:00')
            if col is None:
                mapday[date + ' 12:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 13:00:00') >= 0 and compareTime(record, date + ' 13:00:59') <= 0:
            col = mapday.get(date + ' 13:00:00')
            if col is None:
                mapday[date + ' 13:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 14:00:00') >= 0 and compareTime(record, date + ' 14:00:59') <= 0:
            col = mapday.get(date + ' 14:00:00')
            if col is None:
                mapday[date + ' 14:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 15:00:00') >= 0 and compareTime(record, date + ' 15:00:59') <= 0:
            col = mapday.get(date + ' 15:00:00')
            if col is None:
                mapday[date + ' 15:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 16:00:00') >= 0 and compareTime(record, date + ' 16:00:59') <= 0:
            col = mapday.get(date + ' 16:00:00')
            if col is None:
                mapday[date + ' 16:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 17:00:00') >= 0 and compareTime(record, date + ' 17:00:59') <= 0:
            col = mapday.get(date + ' 17:00:00')
            if col is None:
                mapday[date + ' 17:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 18:00:00') >= 0 and compareTime(record, date + ' 18:00:59') <= 0:
            col = mapday.get(date + ' 18:00:00')
            if col is None:
                mapday[date + ' 18:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 19:00:00') >= 0 and compareTime(record, date + ' 19:00:59') <= 0:
            col = mapday.get(date + ' 19:00:00')
            if col is None:
                mapday[date + ' 19:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 20:00:00') >= 0 and compareTime(record, date + ' 20:00:59') <= 0:
            col = mapday.get(date + ' 20:00:00')
            if col is None:
                mapday[date + ' 20:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 21:00:00') >= 0 and compareTime(record, date + ' 21:00:59') <= 0:
            col = mapday.get(date + ' 21:00:00')
            if col is None:
                mapday[date + ' 21:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 22:00:00') >= 0 and compareTime(record, date + ' 22:00:59') <= 0:
            col = mapday.get(date + ' 22:00:00')
            if col is None:
                mapday[date + ' 22:00:00'] = day
            else:
                compareDay(col, day)
        elif compareTime(record, date + ' 23:00:00') >= 0 and compareTime(record, date + ' 23:00:59') <= 0:
            col = mapday.get(date + ' 23:00:00')
            if col is None:
                mapday[date + ' 23:00:00'] = day
            else:
                compareDay(col, day)

    return mapday


def compareDay(col={}, day={}):
    if col['memory'] is None:
        col['memory'] = day['memory']
    if col['memory'] is not None and day['memory'] is not None:
        if compareInt(col['memory'], day['memory']) <= 0:
            col['memory'] = day['memory']
    if col['cpu'] is None:
        col['cpu'] = day['cpu']
    if col['cpu'] is not None and day['cpu'] is not None:
        if compareInt(col['cpu'], day['cpu']) <= 0:
            col['cpu'] = day['cpu']
    if col['network_io'] is None:
        col['network_io'] = day['network_io']
    if col['network_io'] is not None and day['network_io'] is not None:
        if compareInt(col['network_io'], day['network_io']) <= 0:
            col['network_io'] = day['network_io']
    if col['disk_io'] is None:
        col['disk_io'] = day['disk_io']
    if col['disk_io'] is not None and day['disk_io'] is not None:
        if compareInt(col['disk_io'], day['disk_io']) <= 0:
            col['disk_io'] = day['disk_io']
    if col['cpu_temp'] is None:
        col['cpu_temp'] = day['cpu_temp']
    if col['cpu_temp'] is not None and day['cpu_temp'] is not None:
        if compareInt(col['cpu_temp'], day['cpu_temp']) <= 0:
            col['cpu_temp'] = day['cpu_temp']
    if col['gpu_temp'] is None:
        col['gpu_temp'] = day['gpu_temp']
    if col['gpu_temp'] is not None and day['gpu_temp'] is not None:
        if compareInt(col['gpu_temp'], day['gpu_temp']) <= 0:
            col['gpu_temp'] = day['gpu_temp']
    return col


def compareInt(a, b):
    return int(a) - int(b)


def compareTime(start, end):
    return datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S').timestamp() - datetime.datetime.strptime(end,
                                                                                                           '%Y-%m-%d %H:%M:%S').timestamp()


async def selectFromCollectorByTime(request):
    map = {}
    listDayMemory = []
    listWeekMemory = []
    listWeekMemoryFinal = []
    listMonthMemory = []
    listAnyDayMemory = []

    listDayCpu = []
    listWeekCpu = []
    listWeekCpuFinal = []
    listMonthCpu = []
    listAnyDayCpu = []

    listDayNetworkIo = []
    listWeekNetworkIo = []
    listWeekNetworkFinal = []
    listMonthNetworkIo = []
    listAnyDayNetworkIo = []

    listDayDiskIo = []
    listWeekDiskIo = []
    listWeekDiskFinal = []
    listMonthDiskIo = []
    listAnyDayDiskIo = []

    listDayGpuTemp = []
    listWeekGpuTemp = []
    listMonthGpuTemp = []
    listAnyDayGpuTemp = []

    listDayCpuTemp = []
    listWeekCpuTemp = []
    listMonthCpuTemp = []
    listAnyDayCpuTemp = []

    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        datetimes = data.get('data')['time']

        if  datetimes == '':
            today = time.strftime("%Y-%m-%d", time.localtime())
            monitor = systemDao.selectToDayFromCollector(today + ' 00:00:00', today + ' 23:59:59')
            mapday = getDayMonitor(monitor)
            listdays = []
            for res in mapday:
                c = {}
                c['record_time'] = res
                c['memory'] = mapday[res]['memory']
                c['cpu'] = mapday[res]['cpu']
                c['network_io'] = mapday[res]['network_io']
                c['disk_io'] = mapday[res]['disk_io']
                c['cpu_temp'] = mapday[res]['cpu_temp']
                c['gpu_temp'] = mapday[res]['gpu_temp']
                listdays.append(c)
            listdays.sort(key=lambda k: k['record_time'])
            if len(listdays) > 0:
                for c in listdays:
                    listm = []
                    listc = []
                    listd = []
                    listn = []
                    listCpuTemp = []
                    listGpuTemp = []
                    if c['memory'] is not None:
                        listm.append(c['record_time'])
                        listm.append(c['memory'])
                        listDayMemory.append(listm)
                    if c['cpu'] is not None:
                        listc.append(c['record_time'])
                        listc.append(c['cpu'])
                        listDayCpu.append(listc)
                    if c['disk_io'] is not None:
                        listd.append(c['record_time'])
                        listd.append(c['disk_io'])
                        listDayDiskIo.append(listd)
                    if c['network_io'] is not None:
                        listn.append(c['record_time'])
                        listn.append(c['network_io'])
                        listDayNetworkIo.append(listn)
                    if c['cpu_temp'] is not None and c['record_time'] is not None:
                        listCpuTemp.append(c['record_time'])
                        listCpuTemp.append(c['cpu_temp'])
                        listDayCpuTemp.append(listCpuTemp)
                    if c['gpu_temp'] is not None and c['record_time'] is not None:
                        listGpuTemp.append(c['record_time'])
                        listGpuTemp.append(c['gpu_temp'])
                        listDayGpuTemp.append(listGpuTemp)

            now = datetime.datetime.now()
        # 本周第一天和最后一天
            this_week_start = str(now - datetime.timedelta(days=now.weekday())).split(" ")[0]
            this_week_end = str(now + datetime.timedelta(days=6 - now.weekday())).split(" ")[0]
            listweek = systemDao.selectToDayFromCollector(this_week_start + ' 00:00:00', this_week_end + ' 23:59:59')
            mapweek = {}
            for res in listweek:
                riqi = str(res['record_time']).split(" ")[0]
                c = mapweek.get(riqi)
                if c is None:
                    mapweek[riqi] = res
                else:
                    compareDay(c, res)
            listweekfinal = []
            for k in mapweek:
                listweekfinal.append(mapweek.get(k))
            listweekfinal.sort(key=lambda k: k['record_time'])
            if len(listweekfinal) > 0:
                for res in listweekfinal:
                    if res['memory'] is not None:
                        listconweekm = []
                        listconweekm.append(res['record_time'])
                        listconweekm.append(res['memory'])
                        listWeekMemory.append(listconweekm)
                    if res['cpu'] is not None:
                        listconweekc = []
                        listconweekc.append(res['record_time'])
                        listconweekc.append(res['cpu'])
                        listWeekCpu.append(listconweekc)
                    if res['disk_io'] is not None:
                        listconweekd = []
                        listconweekd.append(res['record_time'])
                        listconweekd.append(res['disk_io'])
                        listWeekDiskIo.append(listconweekd)
                    if res['network_io'] is not None:
                        listconweekn = []
                        listconweekn.append(res['record_time'])
                        listconweekn.append(res['network_io'])
                        listWeekNetworkIo.append(listconweekn)
                    if res['cpu_temp'] is not None:
                        listconweekCpu = []
                        listconweekCpu.append(res['record_time'])
                        listconweekCpu.append(res['cpu_temp'])
                        listWeekCpuTemp.append(listconweekCpu)
                    if res['gpu_temp'] is not None:
                        listconweekGpu = []
                        listconweekGpu.append(res['record_time'])
                        listconweekGpu.append(res['gpu_temp'])
                        listWeekGpuTemp.append(listconweekGpu)
            now = time.strftime("%Y-%m-%d", time.localtime()).split("-")[0] + '-' + \
            time.strftime("%Y-%m-%d", time.localtime()).split("-")[1]
            listmonth = systemDao.selectToDayFromCollector(now + '-01' + ' 00:00:00', now + '-31' + ' 23:59:59')
            mapmonth = {}
            for res in listmonth:
                c = mapmonth.get(str(res['record_time']).split(" ")[0])
                if c is None:
                    mapmonth[str(res['record_time']).split(" ")[0]] = res
                else:
                    compareDay(c, res)
            listmonthfinal = []
            for k in mapmonth:
                listmonthfinal.append(mapmonth.get(k))
            listmonthfinal.sort(key=lambda k: k['record_time'])
            if len(listmonthfinal) > 0:
                for res in listmonthfinal:
                    listconmonthm = []
                    listconmonthm.append(res['record_time'])
                    listconmonthm.append(res['memory'])
                    listMonthMemory.append(listconmonthm)
                    listconmonthc = []
                    listconmonthc.append(res['record_time'])
                    listconmonthc.append(res['cpu'])
                    listMonthCpu.append(listconmonthc)
                    listconmonthd = []
                    listconmonthd.append(res['record_time'])
                    listconmonthd.append(res['disk_io'])
                    listMonthDiskIo.append(listconmonthd)
                    listconmonthn = []
                    listconmonthn.append(res['record_time'])
                    listconmonthn.append(res['network_io'])
                    listMonthNetworkIo.append(listconmonthn)
                    if res['cpu_temp'] is not None:
                        listconmonthCpuTemp = []
                        listconmonthCpuTemp.append(res['record_time'])
                        listconmonthCpuTemp.append(res['cpu_temp'])
                        listMonthCpuTemp.append(listconmonthCpuTemp)
                    if res['gpu_temp'] is not None:
                        listconmonthGpuTemp = []
                        listconmonthGpuTemp.append(res['record_time'])
                        listconmonthGpuTemp.append(res['gpu_temp'])
                        listMonthGpuTemp.append(listconmonthGpuTemp)
        else:
            listAnyDay = systemDao.selectToDayFromCollector(datetimes + ' 00:00:00', datetimes + ' 23:59:59')
            if len(listAnyDay) > 0:
                mapAnyday = getDayMonitor(listAnyDay)
                listAnydays = []
                for res in mapAnyday:
                    c = {}
                    c['record_time'] = mapAnyday[res]['record_time']
                    c['memory'] = mapAnyday[res]['memory']
                    c['cpu'] = mapAnyday[res]['cpu']
                    c['network_io'] = mapAnyday[res]['network_io']
                    c['disk_io'] = mapAnyday[res]['disk_io']
                    c['cpu_temp'] = mapAnyday[res]['cpu_temp']
                    c['gpu_temp'] = mapAnyday[res]['gpu_temp']
                    listAnydays.append(c)
                listAnydays.sort(key=lambda k: k['record_time'])
                if len(listAnydays) > 0:
                    for res in listAnydays:
                        if res['memory'] is not None:
                            listm = []
                            listm.append(res['record_time'])
                            listm.append(res['memory'])
                            listAnyDayMemory.append(listm)
                        if res['cpu'] is not None:
                            listc = []
                            listc.append(res['record_time'])
                            listc.append(res['cpu'])
                            listAnyDayCpu.append(listc)
                        if res['disk_io'] is not None:
                            listd = []
                            listd.append(res['record_time'])
                            listd.append(res['disk_io'])
                            listAnyDayDiskIo.append(listd)
                        if res['network_io'] is not None:
                            listn = []
                            listn.append(res['record_time'])
                            listn.append(res['network_io'])
                            listAnyDayNetworkIo.append(listn)
                        if res['cpu_temp'] is not None:
                            listCpuTemp = []
                            listCpuTemp.append(res['record_time'])
                            listCpuTemp.append(res['cpu_temp'])
                            listAnyDayCpuTemp.append(listCpuTemp)
                        if res['gpu_temp'] is not None:
                            listGpuTemp = []
                            listGpuTemp.append(res['record_time'])
                            listGpuTemp.append(res['gpu_temp'])
                            listAnyDayGpuTemp.append(listGpuTemp)
        listcputodayTime = []
        listcputodaytmpvalue = []
        listgputodayTime = []
        listgputodaytmpvalue = []
        for res in listDayCpuTemp:
            listcputodayTime.append(str(res[0]))
            listcputodaytmpvalue.append(int(res[1]))
        for res in listDayGpuTemp:
            listgputodayTime.append(str(res[0]))
            listgputodaytmpvalue.append(int(res[1]))

        listDayMemoryTime = []
        listDayMemoryValue = []
        listDayCpuTime = []
        listDayCpuValue = []
        listDayNetworkTime = []
        listDayNetworkValue = []
        listDayDiskTime = []
        listDayDiskValue = []
        for res in listDayMemory:
            listDayMemoryTime.append(str(res[0]))
            listDayMemoryValue.append(str(res[1]))
        for res in listDayCpu:
            listDayCpuTime.append(str(res[0]))
            listDayCpuValue.append(str(res[1]))
        for res in listDayNetworkIo:
            listDayNetworkTime.append(str(res[0]))
            listDayNetworkValue.append(str(res[1]))
        for res in listDayDiskIo:
            listDayDiskTime.append(str(res[0]))
            listDayDiskValue.append(str(res[1]))

        listWeekMemoryTime = []
        listWeekMemoryValue = []
        listWeekCpuTime = []
        listWeekCpuValue = []
        listWeekNetworkTime = []
        listWeekNetworkValue = []
        listWeekDiskTime = []
        listWeekDiskValue = []
        for res in listWeekMemory:
            listWeekMemoryTime.append(str(res[0]))
            listWeekMemoryValue.append(str(res[1]))
        for res in listWeekCpu:
            listWeekCpuTime.append(str(res[0]))
            listWeekCpuValue.append(str(res[1]))
        for res in listWeekNetworkIo:
            listWeekNetworkTime.append(str(res[0]))
            listWeekNetworkValue.append(str(res[1]))
        for res in listWeekDiskIo:
            listWeekDiskTime.append(str(res[0]))
            listWeekDiskValue.append(str(res[1]))

        listMonthMemoryTime = []
        listMonthMemoryValue = []
        listMonthCpuTime = []
        listMonthCpuValue = []
        listMonthNetworkTime = []
        listMonthNetworkValue = []
        listMonthDiskTime = []
        listMonthDiskValue = []
        for res in listMonthMemory:
            listMonthMemoryTime.append(str(res[0]))
            listMonthMemoryValue.append(str(res[1]))
        for res in listMonthCpu:
            listMonthCpuTime.append(str(res[0]))
            listMonthCpuValue.append(str(res[1]))
        for res in listMonthNetworkIo:
            listMonthNetworkTime.append(str(res[0]))
            listMonthNetworkValue.append(str(res[1]))
        for res in listMonthDiskIo:
            listMonthDiskTime.append(str(res[0]))
            listMonthDiskValue.append(str(res[1]))

        listAnyDayMemoryTime = []
        listAnyDayMemoryValue = []
        listAnyDayCpuTime = []
        listAnyDayCpuValue = []
        listAnyDayNetworkTime = []
        listAnyDayNetworkValue = []
        listAnyDayDiskTime = []
        listAnyDayDiskValue = []
        for res in listAnyDayMemory:
            listAnyDayMemoryTime.append(str(res[0]))
            listAnyDayMemoryValue.append(str(res[1]))
        for res in listAnyDayCpu:
            listAnyDayCpuTime.append(str(res[0]))
            listAnyDayCpuValue.append(str(res[1]))
        for res in listAnyDayNetworkIo:
            listAnyDayNetworkTime.append(str(res[0]))
            listAnyDayNetworkValue.append(str(res[1]))
        for res in listAnyDayDiskIo:
            listAnyDayDiskTime.append(str(res[0]))
            listAnyDayDiskValue.append(str(res[1]))
        for res in listWeekMemory:
            year = int(str(res[0]).split(' ')[0].split('-')[0])
            month = int(str(res[0]).split(' ')[0].split('-')[1])
            day = int(str(res[0]).split(' ')[0].split('-')[2])
            listtep = []
            w = int(datetime.datetime(year, month, day).strftime("%w"))
            if w == 0:
                listtep.append('周日')
                listWeekMemoryFinal.append(listtep)
            elif w == 1:
                listtep.append('周一')
                listWeekMemoryFinal.append(listtep)
            elif w == 2:
                listtep.append('周二')
                listWeekMemoryFinal.append(listtep)
            elif w == 3:
                listtep.append('周三')
                listWeekMemoryFinal.append(listtep)
            elif w == 4:
                listtep.append('周四')
                listWeekMemoryFinal.append(listtep)
            elif w == 5:
                listtep.append('周五')
                listWeekMemoryFinal.append(listtep)
            elif w == 6:
                listtep.append('周六')
                listWeekMemoryFinal.append(listtep)
        for res in listWeekCpu:
            year = int(str(res[0]).split(' ')[0].split('-')[0])
            month = int(str(res[0]).split(' ')[0].split('-')[1])
            day = int(str(res[0]).split(' ')[0].split('-')[2])
            listtep = []
            w = int(datetime.datetime(year, month, day).strftime("%w"))
            if w == 0:
                listtep.append('周日')
                listWeekCpuFinal.append(listtep)
            elif w == 1:
                listtep.append('周一')
                listWeekCpuFinal.append(listtep)
            elif w == 2:
                listtep.append('周二')
                listWeekCpuFinal.append(listtep)
            elif w == 3:
                listtep.append('周三')
                listWeekCpuFinal.append(listtep)
            elif w == 4:
                listtep.append('周四')
                listWeekCpuFinal.append(listtep)
            elif w == 5:
                listtep.append('周五')
                listWeekCpuFinal.append(listtep)
            elif w == 6:
                listtep.append('周六')
                listWeekCpuFinal.append(listtep)
        for res in listWeekDiskIo:
            year = int(str(res[0]).split(' ')[0].split('-')[0])
            month = int(str(res[0]).split(' ')[0].split('-')[1])
            day = int(str(res[0]).split(' ')[0].split('-')[2])
            listtep = []
            w = int(datetime.datetime(year, month, day).strftime("%w"))
            if w == 0:
                listtep.append('周日')
                listWeekDiskFinal.append(listtep)
            elif w == 1:
                listtep.append('周一')
                listWeekDiskFinal.append(listtep)
            elif w == 2:
                listtep.append('周二')
                listWeekDiskFinal.append(listtep)
            elif w == 3:
                listtep.append('周三')
                listWeekDiskFinal.append(listtep)
            elif w == 4:
                listtep.append('周四')
                listWeekDiskFinal.append(listtep)
            elif w == 5:
                listtep.append('周五')
                listWeekDiskFinal.append(listtep)
            elif w == 6:
                listtep.append('周六')
                listWeekDiskFinal.append(listtep)
        for res in listWeekNetworkIo:
            year = int(str(res[0]).split(' ')[0].split('-')[0])
            month = int(str(res[0]).split(' ')[0].split('-')[1])
            day = int(str(res[0]).split(' ')[0].split('-')[2])
            listtep = []
            w = int(datetime.datetime(year, month, day).strftime("%w"))
            if w == 0:
                listtep.append('周日')
                listWeekNetworkFinal.append(listtep)
            elif w == 1:
                listtep.append('周一')
                listWeekNetworkFinal.append(listtep)
            elif w == 2:
                listtep.append('周二')
                listWeekNetworkFinal.append(listtep)
            elif w == 3:
                listtep.append('周三')
                listWeekNetworkFinal.append(listtep)
            elif w == 4:
                listtep.append('周四')
                listWeekNetworkFinal.append(listtep)
            elif w == 5:
                listtep.append('周五')
                listWeekNetworkFinal.append(listtep)
            elif w == 6:
                listtep.append('周六')
                listWeekNetworkFinal.append(listtep)
        listcpuweekTime = []
        listcpuweektmpvalue = []
        listgpuweekTime = []
        listgpuweektmpvalue = []
        for res in listWeekCpuTemp:
            year = int(str(res[0]).split(' ')[0].split('-')[0])
            month = int(str(res[0]).split(' ')[0].split('-')[1])
            day = int(str(res[0]).split(' ')[0].split('-')[2])
            w = int(datetime.datetime(year, month, day).strftime("%w"))
            if w == 0:
                listcpuweekTime.append('周日')
            elif w == 1:
                listcpuweekTime.append('周一')
            elif w == 2:
                listcpuweekTime.append('周二')
            elif w == 3:
                listcpuweekTime.append('周三')
            elif w == 4:
                listcpuweekTime.append('周四')
            elif w == 5:
                listcpuweekTime.append('周五')
            elif w == 6:
                listcpuweekTime.append('周六')
            listcpuweektmpvalue.append(str(res[1]))

        for res in listWeekGpuTemp:
            year = int(str(res[0]).split(' ')[0].split('-')[0])
            month = int(str(res[0]).split(' ')[0].split('-')[1])
            day = int(str(res[0]).split(' ')[0].split('-')[2])
            w = int(datetime.datetime(year, month, day).strftime("%w"))
            if w == 0:
                listgpuweekTime.append('周日')
            elif w == 1:
                listgpuweekTime.append('周一')
            elif w == 2:
                listgpuweekTime.append('周二')
            elif w == 3:
                listgpuweekTime.append('周三')
            elif w == 4:
                listgpuweekTime.append('周四')
            elif w == 5:
                listgpuweekTime.append('周五')
            elif w == 6:
                listgpuweekTime.append('周六')
            listgpuweektmpvalue.append(str(res[1]))

        listcpumonthTime = []
        listcpumonthtmpvalue = []
        listgpumonthTime = []
        listgpumonthtmpvalue = []
        for res in listMonthCpuTemp:
            listcpumonthTime.append(str(res[0]))
            listcpumonthtmpvalue.append(str(res[1]))
        for res in listMonthGpuTemp:
            listgpumonthTime.append(str(res[0]))
            listgpumonthtmpvalue.append(str(res[1]))

        listcpuAnyDayTime = []
        listcpuAnyDaytmpvalue = []
        listgpuAnyDayTime = []
        listgpuAnyDaytmpvalue = []
        for res in listAnyDayCpuTemp:
            listcpuAnyDayTime.append(str(res[0]))
            listcpuAnyDaytmpvalue.append(str(res[1]))
        for res in listAnyDayGpuTemp:
            listgpuAnyDayTime.append(str(res[0]))
            listgpuAnyDaytmpvalue.append(str(res[1]))
        map["todayMemoryTime"] = listDayMemoryTime
        map["todayMemoryValue"] = listDayMemoryValue
        map["todayCpuTime"] = listDayCpuTime
        map["todayCpuValue"] = listDayCpuValue
        map["todayNetworkTime"] = listDayNetworkTime
        map["todayNetworkValue"] = listDayNetworkValue
        map["todayDiskTime"] = listDayDiskTime
        map["todayDiskValue"] = listDayDiskValue

        map["weekMemoryTime"] = listWeekMemoryFinal
        map["weekMemoryValue"] = listWeekMemoryValue
        map["weekCpuTime"] = listWeekCpuFinal
        map["weekCpuValue"] = listWeekCpuValue
        map["weekNetworkTime"] = listWeekNetworkFinal
        map["weekNetworkValue"] = listWeekNetworkValue
        map["weekDiskTime"] = listWeekDiskFinal
        map["weekDiskValue"] = listWeekDiskValue

        map["monthMemoryTime"] = listMonthMemoryTime
        map["monthMemoryValue"] = listMonthMemoryValue
        map["monthCpuTime"] = listMonthCpuTime
        map["monthCpuValue"] = listMonthCpuValue
        map["monthNetworkTime"] = listMonthNetworkTime
        map["monthNetworkValue"] = listMonthNetworkValue
        map["monthDiskTime"] = listMonthDiskTime
        map["monthDiskValue"] = listMonthDiskValue

        map["anyDayMemoryTime"] = listAnyDayMemoryTime
        map["anyDayMemoryValue"] = listAnyDayMemoryValue
        map["anyDayCpuTime"] = listAnyDayCpuTime
        map["anyDayCpuValue"] = listAnyDayCpuValue
        map["anyDayNetworkTime"] = listAnyDayNetworkTime
        map["anyDayNetworkValue"] = listAnyDayNetworkValue
        map["anyDayDiskTime"] = listAnyDayDiskTime
        map["anyDayDiskValue"] = listAnyDayDiskValue

        map["todayCpuTempValue"] = listcputodaytmpvalue
        map["todayCpuTempTime"] = listcputodayTime
        map["todayGpuTempValue"] = listgputodaytmpvalue
        map["todayGpuTempTime"] = listgputodayTime

        map["weekCpuTempValue"] = listcpuweektmpvalue
        map["weekCpuTempTime"] = listcpuweekTime
        map["weekGpuTempValue"] = listgpuweektmpvalue
        map["weekGpuTempTime"] = listgpuweekTime

        map["monthCpuTempValue"] = listcpumonthtmpvalue
        map["monthCpuTempTime"] = listcpumonthTime
        map["monthGpuTempValue"] = listgpumonthtmpvalue
        map["monthGpuTempTime"] = listgpumonthTime

        map["anyDayCpuTempValue"] = listcpuAnyDaytmpvalue
        map["anyDayCpuTempTime"] = listcpuAnyDayTime
        map["anyDayGpuTempValue"] = listgpuAnyDaytmpvalue
        map["anyDayGpuTempTime"] = listgpuAnyDayTime

        rt_json = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromMonitor:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# wlan 表
async def selectFromWlanConfig(request):
    rt_json = ""
    try:
        check_db_connect()
        wlan = wlanDao.selectFromWlanConfig()
        rt_json = WebCommon.getNormalJson(wlan, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromWlanConfig:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateWlanSetting(request):
    rt_json = ""
    try:
        check_db_connect()
        wlan = await request.json()
        rt = wlanDao.update(wlan.get('wlan'))
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateWlanSetting:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# ssid 表
async def selectFromSsid(request):
    rt_json = ""
    try:
        check_db_connect()
        ssid = ssidDao.selectFromSsid()
        rt_json = WebCommon.getNormalJson(ssid, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromSsid:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateSsid(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        ssid = data.get('ssid')
        rt = ssidDao.update(ssid)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateSsid:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromSsidById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        ssid = data.get('data')
        ssidDao.delete(ssid['id'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromSsidById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addSsid(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        rt = ssidDao.insertSsid(data)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addSsid:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# dhcp接口

async def selectFromDhcp(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        dhcp = dhcpDao.selectFromDhcp()
        rt_json = WebCommon.getNormalJson(dhcp, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromSsid:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addDhcp(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        rt = dhcpDao.insertDhcp(data.get('data'))
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addSsid:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateDhcp(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        dhcp = data.get('dhcp')
        rt = dhcpDao.update(dhcp)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateSsid:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromDhcpById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        dhcp = data.get('data')
        dhcpDao.delete(dhcp['id'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromDhcpById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# static_ip_config 接口

async def selectFromStaticIpConfig(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        dhcp = staticIpConfigDao.selectFromStaticIpConfig()
        rt_json = WebCommon.getNormalJson(dhcp, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromStaticIpConfig:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addStaticIpConfig(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        rt = staticIpConfigDao.insertStaticIpConfig(data.get('data'))
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addStaticIpConfig:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateStaticIpconfig(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        staticIpConfig = data.get('staticIp')
        rt = staticIpConfigDao.update(staticIpConfig)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateStaticIpconfig:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromStaticIpConfigById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        staticIpConfig = data.get('data')
        staticIpConfigDao.delete(staticIpConfig['id'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromStaticIpConfigById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# table routing_state接口

async def selectFromRoutingStatic(request):
    rt_json = ""
    map = {}
    try:
        check_db_connect()
        data = await request.json()
        route = data.get('data')
        sqlStartIndex = int(route.get('sqlStartIndex'))
        sqlNumber = int(route.get('sqlNumber'))
        sortField = route.get('sortField')
        sortType = route.get('sortType')
        count = routingStaticDao.selectCountFromRoutingStatic()
        routeList = routingStaticDao.selectFromRoutingStatic(sqlStartIndex, sqlNumber, sortField, sortType)
        map['count'] = count
        map['routeList'] = routeList
        rt_json = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromRoutingState:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addRoutingStatic(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        route = data.get('data')
        rt = routingStaticDao.insertRoutingStatic(route)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addRoutingState:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateRoutingStatic(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        route = data.get('route')
        rt = routingStaticDao.update(route)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateRoutingState:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromRoutingStaticById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        route = data.get('data')
        routingStaticDao.delete(route['id'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromRoutingStateById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 访问控制策略接口

async def selectFromAccessControl(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        routeList = accessControlStrategyDao.selectFromAccessControl()
        rt_json = WebCommon.getNormalJson(routeList, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromAccessControl:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addAccessControl(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        access = data.get('data')
        rt = accessControlStrategyDao.insertAccessControl(access)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addAccessControl:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateAccessControl(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        access = data.get('route')
        rt = accessControlStrategyDao.update(access)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateAccessControl:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromAccessControlById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        access = data.get('data')
        accessControlStrategyDao.delete(access['id'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromAccessControlById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


# 访问控制列表接口

async def selectFromAccessControlList(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        routeList = accessControlListDao.selectFromAccessControlList()
        rt_json = WebCommon.getNormalJson(routeList, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromAccessControlList:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addAccessControlList(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        access = data.get('data')
        rt = accessControlStrategyDao.insertAccessControl(access)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addAccessControl:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updateAccessControlList(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        access = data.get('route')
        rt = accessControlStrategyDao.update(access)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updateAccessControl:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromAccessControlListById(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        access = data.get('data')
        accessControlStrategyDao.delete(access['id'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromAccessControlById:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")
    # 用户表增删改查


# 用户

async def selectAllFromUser(request):
    rt_json = ""
    map = {}
    userNameArr = []
    try:
        check_db_connect()
        data = await request.json()
        data = data.get('data')
        sqlStartIndex = int(data.get('sqlStartIndex'))
        sqlNumber = int(data.get('sqlNumber'))
        sortField = data.get('sortField')
        sortType = data.get('sortType')
        userList = userDao.selectAllFromUser(sqlStartIndex, sqlNumber, sortField, sortType)
        for u in userList:
            userNameArr.append(u['user_name'])
        map['count'] = len(userList)
        map['data'] = userList
        map['userNameArr'] = userNameArr
        rt_json = WebCommon.getNormalJson(map, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectAllFromUser:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def addUser(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        user = data.get('data')
        rt = userDao.insertUser(user)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on addUser:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def deleteFromUserByUserName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        user = data.get('data')
        userDao.delete(user['user_name'])
        rt_json = WebCommon.getNormalJson(web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on deleteFromUserByUserName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def updatePasswordByUserName(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        user = data.get('data').get('user')
        rt = userDao.update(user)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on updatePasswordByUserName:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def selectFromUserByUserNameAndPassword(request):
    rt_json = ""
    try:
        check_db_connect()
        data = await request.json()
        user = data.get('data')
        userinfo = user.get('user')
        user_name = userinfo.get('user_name')
        password = userinfo.get('password')
        user = userDao.selectFromUserByUserNameAndPassword(user_name, password)
        if len(user) > 0:
            rt_json = WebCommon.getNormalJson(1, web_error_code.SUCCESS)
        else:
            rt_json = WebCommon.getNormalJson(-1, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on selectFromUserByUserNameAndPassword:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + e)
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")
