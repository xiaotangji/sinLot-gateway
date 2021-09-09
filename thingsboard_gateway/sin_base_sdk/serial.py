
import logging
from .systeminfo import SystemInfo
from inbase import ProductsSerial


class Serial(object):
    __doc__ = "\n    For get 232/485 serial path of InHand's IG serial products\n    "

    def __init__(self):
        self.model_name = self._get_model_name()

    def _get_model_name(self):
        """
        get model name, such as 'IG501L'
        :return: model name
        """
        sysinfo = SystemInfo()
        model_name = sysinfo.get_model_name()
        return model_name

    def get_serial232_path(self):
        """
        get 232 path
        :return: 232 path which is a string
                """
        serial_path = ''
        if ProductsSerial.IG5 in self.model_name:
            serial_path = '/dev/ttyO5'
        else:
            if ProductsSerial.IG9 in self.model_name:
                serial_path = '/dev/ttyO1'
            else:
                if ProductsSerial.IG502 in self.model_name:
                    serial_path = '/dev/ttyO1'
                else:
                    logging.warn('unknown product, model name: %s' % (
                     self.model_name,))
        return serial_path

    def get_serial485_path(self):
        """
        get 485 path
        :return: 485 path which is a string
        """
        serial_path = ''
        if ProductsSerial.IG5 in self.model_name:
            serial_path = '/dev/ttyO1'
        else:
            if ProductsSerial.IG9 in self.model_name:
                serial_path = '/dev/ttyO3'
            else:
                if ProductsSerial.IG502 in self.model_name:
                    serial_path = '/dev/ttyO3'
                else:
                    logging.warn('unknown product, model name: %s' % (
                     self.model_name,))
        return serial_path


if __name__ == '__main__':
    serial = Serial()
    print('232 path: %s' % serial.get_serial232_path())
    serial.get_serial485_path()
    print('485 path: %s' % serial.get_serial485_path())