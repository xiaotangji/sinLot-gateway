import simplejson

from thingsboard_gateway.web.web_error_code import *

CODE = 'code'
MESSAGE = 'message'
RESULT = 'result'
DATA = 'data'


class WebCommon:

    @staticmethod
    def getErrorJson(code, message):
        error_dict = {'error': {CODE: code, MESSAGE: message}}
        return simplejson.dumps(error_dict)

    @staticmethod
    def getNormalFalseJson(code=None, message=None):
        code = INTERNAL_EXCEPTION if code is None else code
        normal_false_dict = {RESULT: False, CODE: code, MESSAGE: message}
        return simplejson.dumps(normal_false_dict)

    @staticmethod
    def getNormalJson(data=None, message=None):
        message = "" if message is None else message
        normal_dict = {RESULT: True, DATA: data, MESSAGE: message}
        return simplejson.dumps(normal_dict, indent=4, sort_keys=True, default=str)

    @staticmethod
    def getOkJson(message):
        ok_dict = {RESULT: True, MESSAGE: message}
        return simplejson.dumps(ok_dict)
        pass

