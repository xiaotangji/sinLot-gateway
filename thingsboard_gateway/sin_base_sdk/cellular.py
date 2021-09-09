
from inbase import BaseRestful
import json, requests, re


class Cellular(BaseRestful):
    __doc__ = '\n    Get Cellular info\n    '

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRestful.__init__(self, ip=ip, port=port)
        else:
            BaseRestful.__init__(self)
        self.modem_url = self.url_base + '/v1/cellular/modem/status'
        self.network_url = self.url_base + '/v1/cellular/network/status'
        self.netwatcher_url = self.url_base + '/v1/netwatcher/keepalive'
        self.config_url = self.url_base + '/v1/cellular/config'
        self.send_sms_url = self.url_base + '/v1/cellular/sms/send/message1'

    def get_modem(self):
        """
        get modem info
        :return:
            {
            "active_sim": "SIM 1",
            "imei_code": "862808034761323",
            "imsi_code": "",
            "iccid_code": "",
            "phone_number": "",
            "signal_level": 0,
            "dbm": 113,
            "rerp": 0,
            "rerq": 0,
            "register_status": 0,
            "operator": "",
            "apns": "",
            "network_type": "",
            "lac": "",
            "cell_id": ""
            }
        """
        return self.get_url_info(self.modem_url)

    def get_network(self):
        """
        get network info
        :return:
        [
            {
            "status": 0,
            "ip_addr": "0.0.0.0",
            "netmask": "0.0.0.0",
            "gateway": "0.0.0.0",
            "dns": "0.0.0.0",
            "mtu": 1500,
            "connect_time": 0
            },
        ]
        """
        return self.get_url_info(self.network_url)

    def parse_sms_result(self, r):
        try:
            data = json.loads(r.text)
        except Exception:
            return -1
        else:
            if 'error_code' in data:
                error_code = {-1:'Open serial failed',  -2:'System error', 
                 -3:'System error', 
                 -4:'Invalid parameter', 
                 -5:'Invalid parameter', 
                 -6:'Invalid parameter', 
                 -7:'Temporary failed', 
                 -8:'Message exceed 160 bytes', 
                 -9:'Phone number exceed 20 bytes', 
                 -10:'Invalid phone number'}
                err_num = data['error_code']
                if err_num == 0:
                    return 0
                    if err_num in error_code:
                        raise Exception(error_code[err_num])
                else:
                    raise Exception(data)
            else:
                raise Exception(data)

    def put_requests(self, url, json_data):
        r = requests.put(url, data=(json.dumps(json_data)), headers=(self.headers))
        return r

    def including_chin(self, str_data):
        chin_mod = re.compile(u'[\u4e00-\u9fa5]')
        is_chinese = chin_mod.search('%s' % str_data)
        return is_chinese

    def send_sms(self, data=''):
        """
        :param data
            {
            "sms_mode": 1,   # 0: pdu, 1: text
            "phone_number": "177xxxx8919",
            "sms_content": "hello,world"
            }
        :return:
            0 : ok, -1: failed
        """
        if not isinstance(data, dict):
            raise KeyError('Invalid payload')
        else:
            pdu, text = (0, 1)
            if 'sms_mode' not in data:
                data['sms_mode'] = 1
            if data['sms_mode'] not in [pdu, text]:
                raise KeyError('Invalid sms_mode')
            if data['sms_mode'] == 1:
                invalid_str = '`~^[]{}|'
                for inv in invalid_str:
                    if inv in data['sms_content']:
                        raise KeyError('sms_content can not including %s' % invalid_str)

            if not (('phone_number' not in data or isinstance)(data['phone_number'], str) and data['phone_number']):
                raise KeyError('Invalid phone_number')
            if len(data['phone_number']) > 20:
                raise KeyError('Phone number exceed 20 bytes')
            if not (('sms_content' not in data or isinstance)(data['sms_content'], str) and data['sms_content']):
                raise KeyError('Invalid sms_content')
            if len(data['sms_content']) > 160:
                raise KeyError('sms_content too long')
            if data['sms_mode'] == text:
                is_chinese = self.including_chin(data['sms_content'])
                if is_chinese is not None:
                    raise KeyError('Do not support Chinese characters')
        r = self.put_requests(self.send_sms_url, data)
        return self.parse_sms_result(r)

    def get_signal_level(self):
        return self.get_single_item_info(self.modem_url, 'signal_level')

    def get_dbm(self):
        return self.get_single_item_info(self.modem_url, 'dbm')

    def get_active_sim(self):
        return self.get_single_item_info(self.modem_url, 'active_sim')

    def get_imei_code(self):
        return self.get_single_item_info(self.modem_url, 'imei_code')

    def get_imsi_code(self):
        return self.get_single_item_info(self.modem_url, 'imsi_code')

    def get_iccid_code(self):
        return self.get_single_item_info(self.modem_url, 'iccid_code')

    def get_phone_number(self):
        return self.get_single_item_info(self.modem_url, 'phone_number')

    def get_rerp(self):
        return self.get_single_item_info(self.modem_url, 'rerp')

    def get_rerq(self):
        return self.get_single_item_info(self.modem_url, 'rerq')

    def get_register_status(self):
        return self.get_single_item_info(self.modem_url, 'register_status')

    def get_operator(self):
        return self.get_single_item_info(self.modem_url, 'operator')

    def get_apns(self):
        return self.get_single_item_info(self.modem_url, 'apns')

    def get_network_type(self):
        return self.get_single_item_info(self.modem_url, 'network_type')

    def get_lac(self):
        return self.get_single_item_info(self.modem_url, 'lac')

    def get_cell_id(self):
        return self.get_single_item_info(self.modem_url, 'cell_id')


if __name__ == '__main__':
    cellular = Cellular()
    modem = cellular.get_modem()
    print('get_modem: %s' % modem)
    netwatcher = cellular.get_netwatcher()
    print('netwatcher : %s' % netwatcher)