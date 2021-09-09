#     Copyright 2021. ThingsBoard
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import logging
import simplejson
from abc import ABC, abstractmethod

from thingsboard_gateway.connectors.connector_extension import ConnectorExtension
from thingsboard_gateway.db_access.device_dao import DeviceDao
from thingsboard_gateway.db_access.device_variable_dao import DeviceVariableDao
from thingsboard_gateway.gateway.constants import CONFIG_DEVICES_SECTION_PARAMETER

log = logging.getLogger("connector")


class Connector(ABC):
    def __init__(self):
        self.device_dao = DeviceDao()
        self.device_variable_dao = DeviceVariableDao()
        self.connector_extension = ConnectorExtension()

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    # @abstractmethod
    # def update_connector(self, config):
    #     pass

    @abstractmethod
    def remove_device(self, device_name):
        pass

    def reload_device_variable(self, device_name):
        device_dict = self.load_device_variable(device_name)
        self.load_single_device_convert(device_dict)

    def load_all_devices(self, connector_name):
        try:
            # 加载属于某个连接器的变量
            device_section_parameter = self.load_connector_variable(connector_name)
            # for device in self.__server_config[CONFIG_DEVICES_SECTION_PARAMETER]:
            for device in device_section_parameter[CONFIG_DEVICES_SECTION_PARAMETER]:
                self.load_single_device_convert(device)
        except Exception as e:
            log.exception(e)

    # 加载属于当前连接器的所有设备变量
    def load_connector_variable(self, connector_name):
        connector_var_dict = {CONFIG_DEVICES_SECTION_PARAMETER: []}
        device_name_list = self.device_dao.get_device_name_list(connector_name)
        for device_name in device_name_list:
            device_dict = self.load_device_variable(device_name)
            connector_var_dict[CONFIG_DEVICES_SECTION_PARAMETER].append(device_dict)
        return connector_var_dict

    # 加载属于某个设备的所有变量
    def load_device_variable(self, device_name):
        device_dict = {}
        device_parameter = {}

        connect_name = self.device_dao.get_connector_name(device_name)
        device_parameter_json = self.device_dao.get_device_parameter(device_name)
        variable_list = self.device_variable_dao.get_all_by_device_name(device_name)
        var_dict = self.load_variable(variable_list)

        if device_parameter_json:
            device_parameter = simplejson.loads(device_parameter_json)

        device_dict.update(device_parameter)
        device_dict.update(var_dict)
        return device_dict

    @abstractmethod
    def load_variable(self, variable_list):
        pass

    @abstractmethod
    def load_single_device_convert(self, device):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def is_connected(self):
        pass

    @abstractmethod
    def on_attributes_update(self, content):
        pass

    @abstractmethod
    def server_side_rpc_handler(self, content):
        pass
