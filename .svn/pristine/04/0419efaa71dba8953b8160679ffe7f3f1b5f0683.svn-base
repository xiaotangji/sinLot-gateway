
from inbase import BaseRestful
INVALID_ARGUMENT_ERROR = {'results': {'error_code':-22,  'error':'Invalid argument'}}


class L2TP(BaseRestful):
    __doc__ = '\n    Get/Set l2tp\n    '

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRestful.__init__(self, ip=ip, port=port)
        else:
            BaseRestful.__init__(self)
        self.get_l2tpv3_url = self.url_base + '/v1/ve/interface/shutdown/get'
        self.set_l2tpv3_url = self.url_base + '/v1/ve/interface/shutdown/put'
        self.get_l2tpv2_url = self.url_base + '/v1/vp/interface/shutdown/get'
        self.set_l2tpv2_url = self.url_base + '/v1/vp/interface/shutdown/put'

    def get_l2tp_status(self, iface_vid: int, version: str='v2'):
        if iface_vid < 1 or iface_vid > 10:
            return INVALID_ARGUMENT_ERROR
        params = {'iface_vid': iface_vid}
        if version == 'v3':
            return self.get_url_info((self.get_l2tpv3_url), params=params)
        if version == 'v2':
            return self.get_url_info((self.get_l2tpv2_url), params=params)
        return INVALID_ARGUMENT_ERROR

    def enable_l2tp(self, iface_vid: int, enable=True, version: str='v2'):
        if iface_vid < 1 or iface_vid > 10:
            return INVALID_ARGUMENT_ERROR
        data = {'iface_vid':iface_vid, 
         'enable':1 if enable else 0}
        if version == 'v3':
            return self.put_url_info(self.set_l2tpv3_url, data)
        if version == 'v2':
            return self.put_url_info(self.set_l2tpv2_url, data)
        return INVALID_ARGUMENT_ERROR


if __name__ == '__main__':
    l2tp = L2TP()
    version = 'v3'
    get_l2tp_status = l2tp.get_l2tp_status(1, version)
    print('get_l2tp_status: %s' % get_l2tp_status)
    print('**************** open ************************')
    enable_l2tp = l2tp.enable_l2tp(1, True, version)
    print('enable_l2tp: %s' % enable_l2tp)
    get_l2tp_status = l2tp.get_l2tp_status(1, version)
    print('get_l2tp_status: %s' % get_l2tp_status)
    print('**************** close ************************')
    enable_l2tp = l2tp.enable_l2tp(1, False, version)
    print('enable_l2tp: %s' % enable_l2tp)
    get_l2tp_status = l2tp.get_l2tp_status(1, version)
    print('get_l2tp_status: %s' % get_l2tp_status)