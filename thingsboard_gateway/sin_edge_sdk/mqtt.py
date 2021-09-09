from base_request import BaseRequest


class MqttComm(BaseRequest):

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRequest.__init__(self, ip=ip, port=port)
        else:
            BaseRequest.__init__(self)


