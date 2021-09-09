
from inbase import APPBasePath
from .systeminfo import SystemInfo
import os


class Config(SystemInfo, APPBasePath):
    __doc__ = '\n    InSystem class in inher from BaseRestful class\n    '

    def __init__(self, ip='', port='', app_name=''):
        """
        :param app_name: app name, required,
            which should be a valid python string
        """
        SystemInfo.__init__(self, ip=ip, port=port)
        self.model_name = self.get_model_name()
        APPBasePath.__init__(self, self.model_name, app_name)
        if not os.path.exists(self.app_path):
            raise FileExistsError('Invalid app_name, do not find app %s' % app_name)


if __name__ == '__main__':
    config = Config(app_name='appname')
    get_app_cfg_path = config.get_app_cfg_path()
    print('get_app_cfg_path: %s' % get_app_cfg_path)