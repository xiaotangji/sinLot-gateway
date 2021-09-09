
from inbase import BaseRestful


class Basic(BaseRestful):
    __doc__ = '\n    reboot device\n    eg:\n\n    '

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRestful.__init__(self, ip=ip, port=port)
        else:
            BaseRestful.__init__(self)
        self.reboot_url = self.url_base + '/v1/system/reboot'

    def reboot(self):
        """
        reboot device
        :return:
            {
            "results":"ok" # "ok" or "failed"
            }
        """
        data = {}
        return self.post_url_info(self.reboot_url, data)


if __name__ == '__main__':
    b = Basic()
    r = b.reboot()
    print('reboot : %s' % r)