
from inbase import BaseRestful
from .systeminfo import SystemInfo


class GPS(BaseRestful):
    __doc__ = '\n    Get GPS status/info\n    '

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRestful.__init__(self, ip=ip, port=port)
        else:
            BaseRestful.__init__(self)
        self.gps_position = self.url_base + '/v1/gps/position/status'
        self.gps_config = self.url_base + '/v1/gps/config'
        self._check_if_supported_gps()

    def _check_if_supported_gps(self):
        sysinfo = SystemInfo()
        pn = sysinfo.get_product_number()
        if '-W' not in pn:
            raise Exception("Invalid Product Number,This device doesn't support GPS")

    def get_position_status(self):
        """
        get gps position status
        :return:
            {
                "gps_enable": 1,   # 1: enable, 0: disenable
                "gps_time": "",
                "latitude": "",
                "longitude": "",
                "speed": "0.0000"
            }
        """
        data = self.get_url_info(self.gps_position)
        if 'latitude' in data:
            if data['latitude']:
                data['latitude'] = data['latitude'].encode('gbk').decode('utf-8')
        if 'longitude' in data:
            if data['longitude']:
                data['longitude'] = data['longitude'].encode('gbk').decode('utf-8')
        return data

    def get_config(self):
        return self.get_url_info(self.gps_config)


if __name__ == '__main__':
    gps = GPS()
    get_position_status = gps.get_position_status()
    print('get gps position: %s' % get_position_status)
    get_config = gps.get_config()
    print('get gps config: %s' % get_config)
    data = {'gps_enable': 1}