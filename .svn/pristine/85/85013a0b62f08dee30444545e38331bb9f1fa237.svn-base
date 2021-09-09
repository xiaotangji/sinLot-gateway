import os, json, logging, requests

PROTOCOL = 'http://'
IP_ADDRESS = '127.0.0.1'
IO_PORT = '8078'


class BaseRequest(object):

    def __init__(self, ip=IP_ADDRESS, port=IO_PORT):
        self.ip_address = ip
        self.port = port
        self.url_base = PROTOCOL + self.ip_address + ':' + str(self.port)
        self.head_file = '/var/run/python/inside.txt'
        self.headers = self.__get_headers()

    def __get_headers(self):
        if os.path.exists(self.head_file):
            with open(self.head_file, 'r') as (f):
                head = f.read()
                if head:
                    self.headers = {'Authorization': 'Bearer ' + head}
                else:
                    raise ValueError('value is invalid')
        else:
            try:
                FileNotFoundError('Can not find head file')
            except NameError:
                print('Can not find head file')

    def error_to_string(self, code):
        error_code = {-4: 'Interrupted system call', -13: 'Permission denied',
                      -16: 'Device Busy',
                      -22: 'Invalid argument',
                      -23: 'Error Request',
                      -110: 'Connection timed out',
                      -113: 'IP Invalid'}
        if code in error_code.keys():
            return error_code.get(code)
        return

    def parse_result(self, r):
        try:
            data = json.loads(r.text)
        except Exception as e:
            try:
                logging.error('Error: %s, %s' % (r.text, e))
                result = self.error_to_string(-22)
                return result
            finally:
                e = None
                del e

        return data

    def get_url_info(self, url, params=''):
        r = requests.get(url, params=params, headers=self.headers)
        return self.parse_result(r)

    def put_url_info(self, url, json_data):
        r = requests.put(url, data=(json.dumps(json_data)), headers=self.headers)
        return self.parse_result(r)

    def post_url_info(self, url, json_data):
        data = json.dumps(json_data)
        r = requests.post(url, data=data, headers=self.headers)
        return self.parse_result(r)

