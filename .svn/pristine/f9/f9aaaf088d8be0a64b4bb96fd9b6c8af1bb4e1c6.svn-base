
from inbase import BaseRestful


class SystemInfo(BaseRestful):
    __doc__ = '\n    Get device system info\n    eg:\n        "language": "Chinese",\n        "hostname": "EdgeGateway",\n        "model_name": "IG501L",\n        "oem_name": "inhand",\n        "serial_number": "00000000",\n        "mac_addr1": "00:18:05:10:00:01",\n        "mac_addr2": "00:18:05:10:00:02",\n        "firmware_version": "1.0.0.r11304",\n        "bootloader_version": "2011.09.r11290",\n        "product_number": "TL01",\n        "description": "www.inhandnetworks.com",\n        "auto_save": 1,\n        "encrypt_passwd": 0\n\n    '

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRestful.__init__(self, ip=ip, port=port)
        else:
            BaseRestful.__init__(self)
        self.system_url = self.url_base + '/v1/system/sysinfo'
        self.language = ''
        self.hostname = ''
        self.model_name = ''
        self.oem_name = ''
        self.serial_number = ''
        self.mac_addr1 = ''
        self.mac_addr2 = ''
        self.firmware_version = ''
        self.bootloader_version = ''
        self.product_number = ''
        self.description = ''
        self.auto_save = ''
        self.encrypt_passwd = ''

    def get_system_info(self):
        return self.get_url_info(self.system_url)

    def get_language(self):
        return self.get_single_item_info(self.system_url, 'language')

    def get_hostname(self):
        return self.get_single_item_info(self.system_url, 'hostname')

    def get_model_name(self):
        return self.get_single_item_info(self.system_url, 'model_name')

    def get_oem_name(self):
        return self.get_single_item_info(self.system_url, 'oem_name')

    def get_serial_number(self):
        return self.get_single_item_info(self.system_url, 'serial_number')

    def get_mac_addr1(self):
        return self.get_single_item_info(self.system_url, 'mac_addr1')

    def get_mac_addr2(self):
        return self.get_single_item_info(self.system_url, 'mac_addr2')

    def get_firmware_version(self):
        return self.get_single_item_info(self.system_url, 'firmware_version')

    def get_bootloader_version(self):
        return self.get_single_item_info(self.system_url, 'bootloader_version')

    def get_product_number(self):
        return self.get_single_item_info(self.system_url, 'product_number')

    def get_description(self):
        return self.get_single_item_info(self.system_url, 'description')

    def get_auto_save(self):
        return self.get_single_item_info(self.system_url, 'auto_save')

    def get_encrypt_passwd(self):
        return self.get_single_item_info(self.system_url, 'encrypt_passwd')


if __name__ == '__main__':
    sysinfo = SystemInfo()
    get_serial_number = sysinfo.get_serial_number()
    print('get_serial_number: %s' % get_serial_number)
    get_system_info = sysinfo.get_system_info()
    print('get_system_info: %s' % get_system_info)