import logging

from aiohttp import web
from thingsboard_gateway.web import web_error_code
from thingsboard_gateway.web.web_common import WebCommon
from thingsboard_gateway.gateway.tb_gateway_service import TBGatewayService

log = logging.getLogger('service')
tbgateway_service = TBGatewayService()


async def read_single_tag(request):
    rt_json = ""
    try:
        data = await request.json()
        tag = data.get('data')
        rt = tbgateway_service.read_single_tag(tag)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on read_single_tag:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")


async def write_single_tag(request):
    rt_json = ""
    try:
        data = await request.json()
        tag = data.get('data')
        rt = tbgateway_service.write_single_tag(tag)
        rt_json = WebCommon.getNormalJson(rt, web_error_code.SUCCESS)
    except Exception as e:
        log.error("Error on write_single_tag:")
        log.exception(e)
        rt_json = WebCommon.getNormalFalseJson(message=web_error_code.FAILED + str(e))
    finally:
        return web.Response(content_type='application/json', body=rt_json, charset="utf-8")
