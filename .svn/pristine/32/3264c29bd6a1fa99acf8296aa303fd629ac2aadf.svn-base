import logging
import os
import pathlib
import stat

import paramiko

from thingsboard_gateway.web import web_error_code
from thingsboard_gateway.web.web_common import WebCommon
from aiohttp import web

log = logging.getLogger('service')


async def reboot(request):
    rt_json = ""
    try:
        data = await request.json()
        parameter = data.get('data')
        rt = os.system(parameter['cmd'])
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on reboot:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")
