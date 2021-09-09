
import os, json, logging, requests
PROTOCOL = 'http://'
IP_ADDRESS = '127.0.0.1'
IO_PORT = '9003'


def get_port():
    port_file = '/var/run/python/http_local.port'
    if os.path.exists(port_file):
        try:
            with open(port_file, 'r') as (f):
                port_str = f.read()
                if port_str:
                    if int(port_str) > 65535 or int(port_str) < 0:
                        raise ValueError('The port should be 0~65535')
                    return str(port_str)
        except Exception:
            pass

    return IO_PORT


class BaseRestful(object):

    def __init__(self, ip=IP_ADDRESS, port=get_port()):
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
        error_code = {-4:'Interrupted system call',  -13:'Permission denied', 
         -16:'Device Busy', 
         -22:'Invalid argument', 
         -23:'Error Request', 
         -110:'Connection timed out', 
         -113:'IP Invalid'}
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

        if 'results' in data:
            result = data['results']
            return result
        elif 'error' in data:
            raise Exception(data['error'])
        else:
            raise Exception(data)

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

    def get_single_item_info(self, url, name):
        """
        get single value of which url and which name
        :param url:  restful url
        :param name:  key_word of return value when call get_url_info function
        :return: return '' if name not exist
        """
        url_info = self.get_url_info(url)
        if name in url_info:
            result = url_info[name]
        else:
            result = self.error_to_string(-22)
        return result


class ProductsSerial(object):
    IG9 = 'IG902'
    IG5 = 'IG501'
    IG502 = 'IG502'


class APPBasePath(object):
    __doc__ = '\n    this class should define every path related to mobiuspy lib\n    '

    def __init__(self, model_name, name):
        """
        :param name: app name
        """
        self._model_name = model_name
        self.app_name = name
        self.app_base_path = '/var/user'
        self.set_app_basepath()
        self.app_path = self.app_base_path + '/app/' + self.app_name
        self.app_cfg_path = self.app_base_path + '/cfg/' + self.app_name
        self.app_default_cfg_name = self.app_path + '/config.yaml'
        self.app_log_path = self.app_base_path + '/log/' + self.app_name
        self.app_db_base_path = self.app_base_path + '/data/dbhome'
        self.app_db_path = self.app_db_base_path + '/' + self.app_name
        self.app_run_base_path = '/var/run/python'
        self.app_run_path = self.app_run_base_path + '/' + self.app_name

    def set_app_basepath(self):
        if ProductsSerial.IG9 in self._model_name or ProductsSerial.IG5 in self._model_name or ProductsSerial.IG502 in self._model_name:
            self.app_base_path = '/var/user'

    def get_app_path(self):
        return self.app_path

    def get_app_log_path(self):
        return self.app_log_path

    def get_app_cfg_path(self):
        return self.app_cfg_path

    def get_app_cfg_file(self):
        app_cfg_file = self.app_cfg_path + '/' + self.app_name + '.cfg'
        if os.access(app_cfg_file, os.F_OK):
            return app_cfg_file
        if os.access(self.app_default_cfg_name, os.F_OK):
            return self.app_default_cfg_name
        app_cfg_file = self.app_path + '/config.ini'
        if os.access(app_cfg_file, os.F_OK):
            return app_cfg_file

    def get_default_app_cfg_file(self):
        if os.access(self.app_default_cfg_name, os.F_OK):
            return self.app_default_cfg_name
        return

    def get_app_db_base_path(self):
        return self.app_db_base_path

    def get_app_db_path(self):
        return self.app_db_path

    def get_app_run_path(self):
        return self.app_run_path


if __name__ == '__main__':
    baserestful = BaseRestful()