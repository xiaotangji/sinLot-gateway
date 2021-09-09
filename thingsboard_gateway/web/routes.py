from thingsboard_gateway.web import collect_api_service as collect
from thingsboard_gateway.web import network_api_service as network
from thingsboard_gateway.web import docker_api_service as docker
from thingsboard_gateway.web import edge_sdk_service as edge
from thingsboard_gateway.web import system_api_service as system

import aiohttp_cors


def setup_routes(app):
    # network
    app.router.add_get('/gateway/system/net', network.getEthernetInfo)
    app.router.add_post('/gateway/system/getSystemInfo', network.getSystemInfo)

    # device
    app.router.add_post('/gateway/collect/startConnector', collect.startConnector)
    app.router.add_post('/gateway/collect/stopConnector', collect.stopConnector)
    app.router.add_post('/gateway/collect/updateDeviceVariable', collect.updateDeviceVariable)
    app.router.add_post('/gateway/collect/updateDeviceParameter', collect.updateDeviceParameter)
    app.router.add_post('/gateway/collect/selectAllFromDevice', collect.selectAllFromDevice)
    app.router.add_post('/gateway/collect/addDevice', collect.addDevice)
    app.router.add_post('/gateway/collect/deleteDeviceByDeviceName', collect.deleteDeviceByDeviceName)
    app.router.add_post('/gateway/collect/updateDeviceByDeviceName', collect.updateDeviceByDeviceName)
    app.router.add_post('/gateway/collect/selectAllFromCon', collect.selectAllFromCon)
    app.router.add_post('/gateway/collect/deleteConByconName', collect.deleteConByconName)
    app.router.add_post('/gateway/collect/addCon', collect.addCon)
    app.router.add_post('/gateway/collect/updateConByName', collect.updateConByName)
    app.router.add_post('/gateway/collect/selectAllFromDeviceVariable', collect.selectAllFromDeviceVariable)
    app.router.add_post('/gateway/collect/selectJsonFromDeviceByDeviceName', collect.selectJsonFromDeviceByDeviceName)
    app.router.add_post('/gateway/collect/addDeviceVariable', collect.addDeviceVariable)
    app.router.add_post('/gateway/collect/updateRequestByDeviceName', collect.updateRequestByDeviceName)
    app.router.add_post('/gateway/collect/deleteDeviceVariableById', collect.deleteDeviceVariableById)
    app.router.add_post('/gateway/collect/updateDeviceVariableById', collect.updateDeviceVariableById)
    app.router.add_post('/gateway/collect/selectAllFromTopic', collect.selectAllFromTopic)
    app.router.add_post('/gateway/collect/addTopic', collect.addTopic)
    app.router.add_post('/gateway/collect/deleteFromTopicByTopicName', collect.deleteFromTopicByTopicName)
    app.router.add_post('/gateway/collect/updateTopicByTopicName', collect.updateTopicByTopicName)
    app.router.add_post('/gateway/collect/selectJsonUpdateJsonRpcJsonFromDeviceByDeviceName',
                        collect.selectJsonUpdateJsonRpcJsonFromDeviceByDeviceName)
    app.router.add_post('/gateway/collect/updateMonitorSetting', collect.updateMonitorSetting)
    app.router.add_post('/gateway/collect/selectFromMonitor', collect.selectFromMonitor)
    app.router.add_post('/gateway/collect/selectFromCollectorByTime', collect.selectFromCollectorByTime)
    app.router.add_post('/gateway/collect/addEthernet', network.addEthernet)
    app.router.add_post('/gateway/collect/updateEthernetByName', network.updateEthernetByName)
    app.router.add_post('/gateway/collect/selectFromEthernetByName', network.selectFromEthernetByName)
    app.router.add_post('/gateway/collect/selectFromSlaveIpConfig', network.selectFromSlaveIpConfig)
    app.router.add_post('/gateway/collect/addSlaveIp', network.addSlaveIp)
    app.router.add_post('/gateway/collect/updateSlaveIpById', network.updateSlaveIpById)
    app.router.add_post('/gateway/collect/deleteSlaveById', network.deleteSlaveById)
    app.router.add_post('/gateway/collect/selectFromWlanConfig', collect.selectFromWlanConfig)
    app.router.add_post('/gateway/collect/updateWlanSetting', collect.updateWlanSetting)
    app.router.add_post('/gateway/collect/addSsid', collect.addSsid)
    app.router.add_post('/gateway/collect/deleteFromSsidById', collect.deleteFromSsidById)
    app.router.add_post('/gateway/collect/updateSsid', collect.updateSsid)
    app.router.add_post('/gateway/collect/selectFromSsid', collect.selectFromSsid)
    app.router.add_post('/gateway/collect/selectFromDhcp', collect.selectFromDhcp)
    app.router.add_post('/gateway/collect/addDhcp', collect.addDhcp)
    app.router.add_post('/gateway/collect/updateDhcp', collect.updateDhcp)
    app.router.add_post('/gateway/collect/deleteFromDhcpById', collect.deleteFromDhcpById)
    app.router.add_post('/gateway/collect/selectFromStaticIpConfig', collect.selectFromStaticIpConfig)
    app.router.add_post('/gateway/collect/addStaticIpConfig', collect.addStaticIpConfig)
    app.router.add_post('/gateway/collect/updateStaticIpconfig', collect.updateStaticIpconfig)
    app.router.add_post('/gateway/collect/deleteFromStaticIpConfigById', collect.deleteFromStaticIpConfigById)
    app.router.add_post('/gateway/collect/selectFromRoutingStatic', collect.selectFromRoutingStatic)
    app.router.add_post('/gateway/collect/addRoutingStatic', collect.addRoutingStatic)
    app.router.add_post('/gateway/collect/updateRoutingStatic', collect.updateRoutingStatic)
    app.router.add_post('/gateway/collect/deleteFromRoutingStaticById', collect.deleteFromRoutingStaticById)
    app.router.add_post('/gateway/collect/selectFromAccessControl', collect.selectFromAccessControl)
    app.router.add_post('/gateway/collect/addAccessControl', collect.addAccessControl)
    app.router.add_post('/gateway/collect/updateAccessControl', collect.updateAccessControl)
    app.router.add_post('/gateway/collect/deleteFromAccessControlById', collect.deleteFromAccessControlById)
    app.router.add_post('/gateway/collect/selectFromAccessControlList', collect.selectFromAccessControlList)
    app.router.add_post('/gateway/collect/addAccessControlList', collect.addAccessControlList)
    app.router.add_post('/gateway/collect/updateAccessControlList', collect.updateAccessControlList)
    app.router.add_post('/gateway/collect/deleteFromAccessControlListById', collect.deleteFromAccessControlListById)

    # user
    app.router.add_post('/gateway/collect/addUser', collect.addUser)
    app.router.add_post('/gateway/collect/deleteFromUserByUserName', collect.deleteFromUserByUserName)
    app.router.add_post('/gateway/collect/updatePasswordByUserName', collect.updatePasswordByUserName)
    app.router.add_post('/gateway/collect/selectAllFromUser', collect.selectAllFromUser)
    app.router.add_post('/gateway/collect/selectFromUserByUserNameAndPassword',
                        collect.selectFromUserByUserNameAndPassword)

    # docker
    app.router.add_get('/gateway/docker/getImageList', docker.getImageList)
    app.router.add_get('/gateway/docker/getContainerList', docker.getContainerList)
    app.router.add_post('/gateway/docker/removeImage', docker.removeImage)
    app.router.add_post('/gateway/docker/createContainer', docker.createContainer)
    app.router.add_post('/gateway/docker/startContainer', docker.startContainer)
    app.router.add_post('/gateway/docker/stopContainer', docker.stopContainer)
    app.router.add_post('/gateway/docker/restartContainer', docker.restartContainer)
    app.router.add_post('/gateway/docker/removeContainer', docker.removeContainer)
    app.router.add_post('/gateway/docker/buildImage', docker.buildImage)

    # system

    app.router.add_post('/gateway/system/reboot', system.reboot)
    # edge sdk
    app.router.add_post('/gateway/edge/readSingleTag', edge.read_single_tag)
    app.router.add_post('/gateway/edge/writeSingleTag', edge.write_single_tag)

    # # `aiohttp_cors.setup` returns `aiohttp_cors.CorsConfig` instance.
    # # The `cors` instance will store CORS configuration for the
    # # application.
    # cors = aiohttp_cors.setup(app)
    #
    # # To enable CORS processing for specific route you need to add
    # # that route to the CORS configuration object and specify its
    # # CORS options.
    # resource = cors.add(app.router.add_resource("/python/gateway/collect/addCon"))
    # route = cors.add(
    #     resource.add_route("POST", collect.addCon), {
    #         "*": aiohttp_cors.ResourceOptions(
    #             allow_credentials=True,
    #             expose_headers="*",
    #             allow_headers="*",
    #             max_age=3600,
    #         )
    #     })
