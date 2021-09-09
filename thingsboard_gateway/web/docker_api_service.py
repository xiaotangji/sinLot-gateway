import logging
import os
import pathlib
import stat

import paramiko

from thingsboard_gateway.sin_docker.docker_manager import DockerManager
from thingsboard_gateway.web import web_error_code
from thingsboard_gateway.web.web_common import WebCommon
from aiohttp import web

docker_manager = DockerManager()
log = logging.getLogger('service')


async def getImageList(request):
    rt_json = ""
    lst = []
    try:
        images = docker_manager.image_list()
        for image in images:
            image_dict = {}
            image_dict.update({"name": image.attrs['RepoTags'][0]})
            image_dict.update({"id": image.attrs['Id']})
            image_dict.update({"tag": image.attrs['RepoTags'][0].split(':')[1]})
            image_dict.update({"createTime": image.attrs['Created']})
            image_dict.update({"size": image.attrs['Size']})
            lst.append(image_dict)

        rt_json = WebCommon.getNormalJson(lst, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on getImageList:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def getContainerList(request):
    rt_json = ""
    lst = []
    try:
        containers = docker_manager.container_list(all=True)
        for container in containers:
            container_dict = {}
            container_dict.update({"containerName": container.name})
            container_dict.update({"containerId": container.attrs['Id']})
            container_dict.update({"imageId": container.attrs['Image']})
            image = docker_manager.image_one(container.attrs['Image'])
            if image:
                container_dict.update({"imageName": container.image.tags[0]})
            else:
                container_dict.update({"imageName": "None"})
            container_dict.update({"commandPath": container.attrs['Path']})
            container_dict.update({"createTime": container.attrs['Created']})
            container_dict.update({"status": container.status})
            lst.append(container_dict)
        rt_json = WebCommon.getNormalJson(lst, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on getContainerList:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def buildImage11(request):
    rt_json = ""
    try:
        data = await request.json()
        parameter = data.get('data').get('data')
        # 路径
        if parameter['type'] == 1:
            rt = docker_manager.image_build(path=parameter['Path'], tag=parameter['imageTag'])
            rt_json = WebCommon.getNormalJson(rt[0].tags[0], web_error_code.SUCCESS)
        # 命令行方式
        else:
            rt = os.system(parameter['cmd'])
            rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)

    except Exception as e:
        log.error("Error on buildImage:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def removeImage(request):
    rt_json = ""
    try:
        data = await request.json()
        image = data.get('data')
        rt = docker_manager.image_remove(image['imageName'], False, False)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on removeImage:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def createContainer(request):
    rt_json = ""
    try:
        data = await request.json()
        parameter = data.get('data')
        container = docker_manager.container_create(parameter['imageName'], detach=True)
        rt_json = WebCommon.getNormalJson(container.name, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on createContainer:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def startContainer(request):
    rt_json = ""
    try:
        data = await request.json()
        parameter = data.get('data').get('data')
        rt = docker_manager.container_start(parameter['container_name'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on startContainer:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def stopContainer(request):
    rt_json = ""
    try:
        data = await request.json()
        parameter = data.get('data').get('data')
        rt = docker_manager.container_stop(parameter['container_name'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on stopContainer:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def restartContainer(request):
    rt_json = ""
    try:
        data = await request.json()
        parameter = data.get('data').get('data')
        rt = docker_manager.container_restart(parameter['container_name'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on restartContainer:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def removeContainer(request):
    rt_json = ""
    try:
        data = await request.json()
        container = data.get('data').get('data')
        rt = docker_manager.container_remove(container['container_name'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on removeContainer:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def buildImage(request):
    rt_json = ""
    try:
        dsc_path = '/home/pi/project/dockerfileTest'
        data = await request.json()
        parameter = data.get('data').get('data')
        name = parameter['fileName']
        os.chmod(dsc_path, stat.S_IRWXU)
        content = parameter.get('data')
        ssh = paramiko.SSHClient()  # 创建SSH对象
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if os.path.exists(dsc_path):
            if os.path.isdir(dsc_path):
                f = open(name, 'w+')
                f.write(content)
                ssh.close()
            else:
                print('please input the dir name')
        else:
            print('the path is not exists')

    except Exception as e:
        log.error("Error on buildImage:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")
