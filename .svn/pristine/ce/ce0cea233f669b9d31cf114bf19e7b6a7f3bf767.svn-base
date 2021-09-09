
import logging
from inbase import BaseRestful
from .systeminfo import SystemInfo
SHUT_DOWN_MODE = 'shutdown'
DIGITAL_DRY_CONTACT_MODE = 'drycontact'
DIGITAL_WET_CONTACT_MODE = 'wetcontact'
ANALOG_LOW_A_MODE = '0_20mA'
ANALOG_HIGH_A_MODE = '4_20mA'
ANALOG_LOW_V_MODE = '0_5V'
ANALOG_HIGH_V_MODE = '0_10V'
INPUT_DIRECTION = 'input'
OUTPUT_DIRECTION = 'output'
DRY_CONTACT_HIGH_VALUE = 'HIGH'
DRY_CONTACT_LOW_VALUE = 'LOW'
WET_CONTACT_ON = 'ON'
WET_CONTACT_OFF = 'OFF'


class IO(BaseRestful):

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRestful.__init__(self, ip=ip, port=port)
        else:
            BaseRestful.__init__(self)
        self.url_io_list_get = self.url_base + '/v1/io/list'
        self.url_io_info_get = self.url_base + '/v1/io/info'
        self.url_io_setup_put = self.url_base + '/v1/io/setup'
        self.url_io_all_info_get = self.url_base + '/v1/io/all/info'
        self.url_io_read_get = self.url_base + '/v1/io/read'
        self.url_io_write_get = self.url_base + '/v1/io/write'
        self._check_if_supported_io()
        self._io_list = self.get_io_list()

    def _verify_io_name(self, io_name):
        """
        verify if io name is valid
        :param io_name: io name, string
        :return:
        """
        if io_name in self._io_list:
            return True
        return False

    def _check_if_supported_io(self):
        sysinfo = SystemInfo()
        mn = sysinfo.get_model_name()
        if 'H' not in mn:
            raise Exception("Invalid model_name,This device doesn't support IO")

    def get_io_list(self):
        """
        get all io list, which is a list,
        different device may have diffeent results.
        :return:  eg: ["di1", "di2", "di3", "di4", "do1", "do2", "ai1", "ai2"]
        """
        return self.get_url_info(self.url_io_list_get)

    def get_io_info(self, io_name=''):
        """

        :param io_name: the name of io
        :return:
            {
                "name": "di1",
                "type": "digital input",
                "mode": "shutdown",
                "index": 1,
            }
        """
        if not self._verify_io_name(io_name):
            raise KeyError('Invalid io_name')
        params = {'io_name': io_name}
        return self.get_url_info((self.url_io_info_get), params=params)

    def setup_digital_io(self, io_name='', mode='', type='digital'):
        """
        you should only use this function for di(digital input)
        :param mode:
            SHUT_DOWN_MODE = "shutdown"
            DIGITAL_DRY_CONTACT_MODE = "drycontact"
            DIGITAL_WET_CONTACT_MODE = "wetcontact"
        :return:
            {
                "name": "di1",
                "type": "digital input",
                "mode": "shutdown",
                "index": 1,
            }

        """
        if not self._verify_io_name(io_name):
            raise KeyError('Invalid io_name')
        if mode not in [SHUT_DOWN_MODE,
         DIGITAL_DRY_CONTACT_MODE,
         DIGITAL_WET_CONTACT_MODE]:
            raise KeyError('Invalid mode')
        data = {'io_name':io_name, 
         'direction':INPUT_DIRECTION,  'mode':mode, 
         'type':type}
        return self.put_url_info(self.url_io_setup_put, data)

    def setup_analog_io(self, io_name='', mode='', type='analog'):
        """
        :param mode:
            SHUT_DOWN_MODE = "shutdown"
            ANALOG_LOW_A_MODE = "0_20mA"
            ANALOG_HIGH_A_MODE = "4_20mA"
            ANALOG_LOW_V_MODE = "0_5V"
            ANALOG_HIGH_V_MODE = "0_10V"
        :return:
        {
            "name": "ai1",
            "type": "analog input",
            "mode": "shutdown",
            "index": 1,
        }
        """
        if not self._verify_io_name(io_name):
            raise KeyError('Invalid io_name')
        if mode not in [SHUT_DOWN_MODE, ANALOG_LOW_A_MODE,
         ANALOG_HIGH_A_MODE,
         ANALOG_LOW_V_MODE, ANALOG_HIGH_V_MODE]:
            raise KeyError('Invalid mode')
        data = {'io_name':io_name, 
         'mode':mode,  'type':type}
        return self.put_url_info(self.url_io_setup_put, data)

    def get_all_io_info(self):
        """
        :return:
        {
            "di1": {
                "name": "di1",
                "type": "digital input",
                "mode": "shutdown",
                "index": 1
            },
            "di2": {
                "name": "di2",
                "index": 2,
                "type": "digital input",
                "mode": "shutdown"
            },
            "di3": {
                "name": "di3",
                "index": 3,
                "type": "digital input",
                "mode": "shutdown",
            },
            "di4": {
                "name": "di4",
                "index": 4,
                "type": "digital input",
                "mode": "shutdown",
            },
            "do1": {
                "name": "do1",
                "index": 1,
                "type": "digital output"
            },
            "do2": {
                "name": "do2",
                "index": 2,
                "type": "digital output"
            },
            "ai1": {
                "name": "ai1",
                "index": 1,
                "type": "analog input"
            },
            "ai2": {
                "name": "ai2",
                "index": 2,
                "type": "analog input"
            }
        }
        """
        return self.get_url_info(self.url_io_all_info_get)

    def read_io(self, io_name=''):
        """
        :param    io_name: the name of io
        :return:
            # read digital io
            "HIGH","LOW"(for drycontact)
            "ON","OFF"(for wetcontact)

            # read analog io
            "0_20mA"(for ANALOG_LOW_A_MODE)
            "4_20mA"(for ANALOG_HIGH_A_MODE)
            "0_5V"(ANALOG_LOW_V_MODE)
            "0_10V"(ANALOG_HIGH_V_MODE)
        """
        if not self._verify_io_name(io_name):
            raise KeyError('Invalid io_name')
        params = {'io_name': io_name}
        return self.get_url_info((self.url_io_read_get), params=params)

    def write_io(self, io_name='', value=''):
        """
        you should only use this function for do,
        and the value should be HIGH/LOW
        :param io_name: the name of io
        :param value:
            DRY_CONTACT_HIGH_VALUE = "HIGH"
            DRY_CONTACT_LOW_VALUE = "LOW"
        :return:   True / False
        """
        if not self._verify_io_name(io_name):
            raise KeyError('Invalid io_name')
        if value not in [DRY_CONTACT_HIGH_VALUE, DRY_CONTACT_LOW_VALUE]:
            raise KeyError('Invalid value')
        data = {'io_name':io_name, 
         'value':value}
        return self.put_url_info(self.url_io_write_get, data)


if __name__ == '__main__':
    io = IO()
    io_list = io.get_io_list()
    logging.info('response: %s , type: %s' % (io_list, type(io_list)))
    io_info = io.get_io_info(io_name=(io_list[1]))
    logging.info('io_info: %s' % io_info)
    sdi = io.setup_digital_io(io_name=(io_list[1]), mode=DIGITAL_DRY_CONTACT_MODE)
    logging.info('sdi: %s' % sdi)
    sni = io.setup_analog_io(io_name=(io_list[7]), mode=ANALOG_HIGH_V_MODE)
    logging.info('io.setup_analog_io: %s' % sni)
    all_io_info = io.get_all_io_info()
    logging.info('all_io_info: %s' % all_io_info)
    ri = io.read_io(io_name=(io_list[0]))
    logging.info('ri io_list[0]: %s' % ri)
    ri_digital = io.read_io(io_name=(io_list[1]))
    logging.info('ri ri_digital io_list[1]: %s' % ri_digital)
    ri_analog = io.read_io(io_name=(io_list[7]))
    logging.info('ri ri_analog io_list[7]: %s' % ri_analog)
    wi = io.write_io(io_name=(io_list[4]), value=DRY_CONTACT_HIGH_VALUE)
    logging.info('wi: %s' % wi)
    import time
    time.sleep(4)
    wi = io.write_io(io_name=(io_list[4]), value=DRY_CONTACT_LOW_VALUE)
    logging.info('wi: %s' % wi)
    ri = io.read_io(io_name=(io_list[1]))
    logging.info('ri: %s' % ri)