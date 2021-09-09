import time
import threading
from random import choice
from string import ascii_lowercase


from thingsboard_gateway.tb_utility.tb_loader import TBModuleLoader
from thingsboard_gateway.connectors.connector import Connector, log
from thingsboard_gateway.connectors.mitsubishi.constants import *
from thingsboard_gateway.connectors.hslcommunication.hsl_communication import MelsecMcNet, MelsecMcAsciiNet, MelsecA1ENet
from thingsboard_gateway.connectors.mitsubishi.mitsubishi_plc_enum import MitsubishiPlcConnectType
from thingsboard_gateway.connectors.mitsubishi.bytes_mplc_uplink_converter import BytesMPlcUplinkConverter
from thingsboard_gateway.connectors.mitsubishi.bytes_mplc_downlink_converter import BytesMPlcDownlinkConverter

CONVERTED_DATA_SECTIONS = [ATTRIBUTES_PARAMETER, TELEMETRY_PARAMETER]


class MitsubishiPlcConnector(Connector, threading.Thread):

    def __init__(self, gateway, config, connector_type):
        self.statistics = {STATISTIC_MESSAGE_RECEIVED_PARAMETER: 0,
                           STATISTIC_MESSAGE_SENT_PARAMETER: 0}
        Connector.__init__(self)
        threading.Thread.__init__(self)

        self.__gateway = gateway
        self._connector_type = connector_type
        self.__server_config = config.get(CONFIG_SERVER_SECTION_PARAMETER)
        self.__current_master, self.__available_functions = self.__configure_master()

        self.__devices = {}
        self.__connector_name = config.get("name", 'Mitsubishi Plc Default ' + ''.join(choice(ascii_lowercase) for _ in range(5)))
        self.setName(self.__connector_name)
        # 加载设备
        self.load_all_devices(self.__connector_name)
        self.__connected = False
        self.__stopped = False
        self.daemon = True

    def is_connected(self):
        return self.__connected

    # def update_connector(self, config):
    #     self.__server_config = config.get(CONFIG_SERVER_SECTION_PARAMETER)
    #     self.setName(config.get("name", 'Mitsubishi Plc Default ' + ''.join(choice(ascii_lowercase) for _ in range(5))))
    #     self.load_all_devices(self.__server_config.get("name"))

    def remove_device(self, device_name):
        if self.__devices.get(device_name):
            del self.__devices[device_name]

    def open(self):
        self.__stopped = False
        self.start()
        log.info("Starting Mitsubishi Plc connector")

    def run(self):
        self.__connect_to_current_master()
        # self.__connected = True

        while True:
            time.sleep(1)
            self.__process_devices()
            if self.__stopped:
                break

    def load_variable(self, variable_list):
        dict = {"timeseries": [],
                "attributes": []
                }

        for variable in variable_list:
            for k, v in dict.items():
                if variable['tag_category'] == k:
                    temp_dict = {"tag": variable['tag_name'],
                                 "type": variable['tag_type'],
                                 "functionCode": variable['function_code'],
                                 "objectsCount": variable['count'],
                                 "address": variable['address'],
                                 variable['data_calculation']: variable['calculation_factor']
                                 }

                    dict[k].append(temp_dict)
        return dict

    def load_single_device_convert(self, device):
        try:
            if self.__server_config.get(UPLINK_PREFIX + CONVERTER_PARAMETER) is not None:
                converter = TBModuleLoader.import_module(self._connector_type,
                                                         self.__server_config[UPLINK_PREFIX + CONVERTER_PARAMETER])(device)
            else:
                converter = BytesMPlcUplinkConverter(device)
            if self.__server_config.get(DOWNLINK_PREFIX + CONVERTER_PARAMETER) is not None:
                downlink_converter = TBModuleLoader.import_module(self._connector_type, self.__server_config[
                    DOWNLINK_PREFIX + CONVERTER_PARAMETER])(device)
            else:
                downlink_converter = BytesMPlcDownlinkConverter(device)
            if device.get(DEVICE_NAME_PARAMETER) not in self.__gateway.get_devices():
                self.__gateway.add_device(device.get(DEVICE_NAME_PARAMETER), {CONNECTOR_PARAMETER: self},
                                          device_type=device.get(DEVICE_TYPE_PARAMETER))
            self.__devices[device[DEVICE_NAME_PARAMETER]] = {CONFIG_SECTION_PARAMETER: device,
                                                             UPLINK_PREFIX + CONVERTER_PARAMETER: converter,
                                                             DOWNLINK_PREFIX + CONVERTER_PARAMETER: downlink_converter,
                                                             NEXT_PREFIX + ATTRIBUTES_PARAMETER + CHECK_POSTFIX: 0,
                                                             NEXT_PREFIX + TIMESERIES_PARAMETER + CHECK_POSTFIX: 0,
                                                             TELEMETRY_PARAMETER: {},
                                                             ATTRIBUTES_PARAMETER: {},
                                                             LAST_PREFIX + TELEMETRY_PARAMETER: {},
                                                             LAST_PREFIX + ATTRIBUTES_PARAMETER: {},
                                                             CONNECTION_ATTEMPT_PARAMETER: 0
                                                             }
        except Exception as e:
            log.exception(e)

    def close(self):
        self.__stopped = True
        self.__stop_connections_to_masters()
        log.info('%s has been stopped.', self.get_name())
        pass

    def get_name(self):
        return self.name

    def on_attributes_update(self, content):
        pass

    def server_side_rpc_handler(self, content):
        pass

    def __configure_master(self, config=None):
        current_config = self.__server_config if config is None else config

        host = current_config[HOST_PARAMETER] if current_config.get(HOST_PARAMETER) is not None else self.__server_config.get(
            HOST_PARAMETER, "localhost")
        try:
            port = int(current_config[PORT_PARAMETER]) if current_config.get(
                PORT_PARAMETER) is not None else int(self.__server_config.get(PORT_PARAMETER, 6000))
        except ValueError:
            port = current_config[PORT_PARAMETER] if current_config.get(
                PORT_PARAMETER) is not None else self.__server_config.get(PORT_PARAMETER, 6000)
        timeout = current_config[TIMEOUT_PARAMETER] if current_config.get(
            TIMEOUT_PARAMETER) is not None else self.__server_config.get(TIMEOUT_PARAMETER, 35)
        type = current_config[TYPE_PARAMETER] if current_config.get(TYPE_PARAMETER) is not None else self.__server_config.get(
            TYPE_PARAMETER, MitsubishiPlcConnectType.BINARY.name)
        if type.upper() == MitsubishiPlcConnectType.BINARY.name:
            master = MelsecMcNet(host, port)
        elif type.upper() == MitsubishiPlcConnectType.ASCII.name:
            master = MelsecMcAsciiNet(host, port)
        elif type.upper() == MitsubishiPlcConnectType.A1E:
            master = MelsecA1ENet(host, port)
        else:
            raise Exception("Invalid Plc transport type.")

        available_functions = {
            "ReadBool": master.ReadBool,
            "WriteBool": master.WriteBool,
            "ReadInt16": master.ReadInt16,
            "WriteInt16": master.WriteInt16,
            "ReadUInt16": master.ReadUInt16,
            "WriteUInt16": master.WriteUInt16,
            "ReadInt32": master.ReadInt32,
            "WriteInt32": master.WriteInt32,
            "ReadUInt32": master.ReadUInt32,
            "WriteUInt32": master.WriteUInt32,
            "ReadInt64": master.ReadInt64,
            "WriteInt64": master.WriteInt64,
            "ReadUInt64": master.ReadUInt64,
            "WriteUInt64": master.WriteUInt64,
            "ReadFloat": master.ReadFloat,
            "WriteFloat": master.WriteFloat,
            "ReadDouble": master.ReadDouble,
            "WriteDouble": master.WriteDouble,
            "ReadString": master.ReadString,
            "WriteString": master.WriteString,
        }
        return master, available_functions

    def __connect_to_current_master(self, device=None):
        connect_attempt_count = 5
        connect_attempt_time_ms = 100
        wait_after_failed_attempts_ms = 300000

        if device is None and len(self.__devices) == 0:
            return
        if device is None:
            device = list(self.__devices.keys())[0]
        if self.__devices[device].get(MASTER_PARAMETER) is None:
            self.__devices[device][MASTER_PARAMETER], self.__devices[device][
                AVAILABLE_FUNCTIONS_PARAMETER] = self.__configure_master(
                self.__devices[device][CONFIG_SECTION_PARAMETER])
        if self.__devices[device][MASTER_PARAMETER] != self.__current_master:
            self.__current_master = self.__devices[device][MASTER_PARAMETER]
            self.__available_functions = self.__devices[device][AVAILABLE_FUNCTIONS_PARAMETER]
        connect_attempt_count = self.__devices[device][CONFIG_SECTION_PARAMETER].get(CONNECT_ATTEMPT_COUNT_PARAMETER,
                                                                                     connect_attempt_count)
        if connect_attempt_count < 1:
            connect_attempt_count = 1
        connect_attempt_time_ms = self.__devices[device][CONFIG_SECTION_PARAMETER].get(
            CONNECT_ATTEMPT_TIME_MS_PARAMETER, connect_attempt_time_ms)
        if connect_attempt_time_ms < 500:
            connect_attempt_time_ms = 500
        wait_after_failed_attempts_ms = self.__devices[device][CONFIG_SECTION_PARAMETER].get(
            WAIT_AFTER_FAILED_ATTEMPTS_MS_PARAMETER, wait_after_failed_attempts_ms)
        if wait_after_failed_attempts_ms < 1000:
            wait_after_failed_attempts_ms = 1000
        current_time = time.time() * 1000
        if not self.__connected:
            if self.__devices[device][CONNECTION_ATTEMPT_PARAMETER] >= connect_attempt_count and \
                    current_time - self.__devices[device][
                LAST_CONNECTION_ATTEMPT_TIME_PARAMETER] >= wait_after_failed_attempts_ms:
                self.__devices[device][CONNECTION_ATTEMPT_PARAMETER] = 0
            while not self.__connected \
                    and self.__devices[device][CONNECTION_ATTEMPT_PARAMETER] < connect_attempt_count \
                    and current_time - self.__devices[device].get(LAST_CONNECTION_ATTEMPT_TIME_PARAMETER,
                                                                  0) >= connect_attempt_time_ms:
                self.__devices[device][CONNECTION_ATTEMPT_PARAMETER] = self.__devices[device][
                                                                           CONNECTION_ATTEMPT_PARAMETER] + 1
                self.__devices[device][LAST_CONNECTION_ATTEMPT_TIME_PARAMETER] = current_time
                log.debug("Plc trying connect to %s", device)
                self.__connected = self.__current_master.ConnectServer().IsSuccess
                if self.__devices[device][CONNECTION_ATTEMPT_PARAMETER] == connect_attempt_count:
                    log.warn("Maximum attempt count (%i) for device \"%s\" - encountered.", connect_attempt_count,
                             device)
                #     time.sleep(connect_attempt_time_ms / 1000)
                # if not self.__current_master.is_socket_open():
        if self.__devices[device][CONNECTION_ATTEMPT_PARAMETER] >= 0 and self.__connected:
            self.__devices[device][CONNECTION_ATTEMPT_PARAMETER] = 0
            self.__devices[device][LAST_CONNECTION_ATTEMPT_TIME_PARAMETER] = current_time
            log.debug("Plc connected to device %s.", device)

    def __stop_connections_to_masters(self):
        for device in self.__devices:
            self.__devices[device][MASTER_PARAMETER].ConnectClose()

    def __function_to_device(self, config):
        function_code = config.get(FUNCTION_CODE_PARAMETER)
        function_type = config.get(TYPE_PARAMETER)
        result = None
        if function_code.upper() == READ_FUNCTION_CODE.upper():
            result = self.__available_functions[READ_FUNCTION_CODE + function_type](config[ADDRESS_PARAMETER], config.get(OBJECTS_COUNT_PARAMETER))
        elif function_code.upper() == WRITE_FUNCTION_CODE.upper():
            result = self.__available_functions[WRITE_FUNCTION_CODE + function_type](config[ADDRESS_PARAMETER], config[PAYLOAD_PARAMETER])
        else:
            log.error("Unknown Modbus function with code: %i", function_code)
        log.debug("With result %s", str(result))
        if "Exception" in str(result):
            log.exception(result)
        return result

    def __process_devices(self):
        for device in self.__devices:
            current_time = time.time()
            device_responses = {TIMESERIES_PARAMETER: {},
                                ATTRIBUTES_PARAMETER: {},
                                }
            # to_send = {}
            to_send = {DEVICE_NAME_PARAMETER: {},
                       DEVICE_TYPE_PARAMETER: {},
                       TELEMETRY_PARAMETER: [],
                       ATTRIBUTES_PARAMETER: []
                       }
            try:
                for config_section in device_responses:
                    if self.__devices[device][CONFIG_SECTION_PARAMETER].get(config_section) is not None:
                        current_device_config = self.__devices[device][CONFIG_SECTION_PARAMETER]
                        unit_id = current_device_config[UNIT_ID_PARAMETER]
                        if self.__devices[device][NEXT_PREFIX + config_section + CHECK_POSTFIX] < current_time:
                            self.__connect_to_current_master(device)
                            if not self.__connected or not len(current_device_config[config_section]):
                                continue
                            #  Reading data from device
                            for interested_data in range(len(current_device_config[config_section])):
                                current_data = current_device_config[config_section][interested_data]
                                current_data[DEVICE_NAME_PARAMETER] = device
                                input_data = self.__function_to_device(current_data)
                                device_responses[config_section][current_data[TAG_PARAMETER]] = {
                                    "data_sent": current_data,
                                    "input_data": input_data}

                            log.debug("Checking %s for device %s", config_section, device)
                            self.__devices[device][NEXT_PREFIX + config_section + CHECK_POSTFIX] = current_time + current_device_config[
                                 config_section + POLL_PERIOD_POSTFIX] / 1000
                            log.debug(device_responses)
                            converted_data = {}
                            try:
                                converted_data = self.__devices[device][UPLINK_PREFIX + CONVERTER_PARAMETER].convert(
                                    config=current_device_config,
                                    data=device_responses)
                            except Exception as e:
                                log.error(e)

                            # to_send = {DEVICE_NAME_PARAMETER: converted_data[DEVICE_NAME_PARAMETER],
                            #            DEVICE_TYPE_PARAMETER: converted_data[DEVICE_TYPE_PARAMETER],
                            #            TELEMETRY_PARAMETER: [],
                            #            ATTRIBUTES_PARAMETER: []
                            #            }
                            to_send[DEVICE_NAME_PARAMETER] = converted_data[DEVICE_NAME_PARAMETER]
                            to_send[DEVICE_TYPE_PARAMETER] = converted_data[DEVICE_TYPE_PARAMETER]

                            if converted_data and current_device_config.get(SEND_DATA_ONLY_ON_CHANGE_PARAMETER):
                                self.statistics[STATISTIC_MESSAGE_RECEIVED_PARAMETER] += 1
                                for converted_data_section in CONVERTED_DATA_SECTIONS:
                                    for current_section_dict in converted_data[converted_data_section]:
                                        for key, value in current_section_dict.items():
                                            if self.__devices[device][LAST_PREFIX + converted_data_section].get(
                                                    key) is None or \
                                                    self.__devices[device][LAST_PREFIX + converted_data_section][key] != value:
                                                self.__devices[device][LAST_PREFIX + converted_data_section][key] = value
                                                to_send[converted_data_section].append({key: value})
                                if not to_send.get(ATTRIBUTES_PARAMETER) and not to_send.get(TELEMETRY_PARAMETER):
                                    log.debug("Data has not been changed.")
                                    continue
                            elif converted_data and current_device_config.get(
                                    SEND_DATA_ONLY_ON_CHANGE_PARAMETER) is None or \
                                    not current_device_config.get(SEND_DATA_ONLY_ON_CHANGE_PARAMETER):
                                self.statistics[STATISTIC_MESSAGE_RECEIVED_PARAMETER] += 1
                                for converted_data_section in CONVERTED_DATA_SECTIONS:
                                    self.__devices[device][LAST_PREFIX + converted_data_section] = converted_data[
                                        converted_data_section]
                                    to_send[converted_data_section] = converted_data[converted_data_section]

                if to_send.get(ATTRIBUTES_PARAMETER) or to_send.get(TELEMETRY_PARAMETER):
                    self.__gateway.save_to_db(self.get_name(), to_send)
                    self.__gateway.send_to_storage(self.get_name(), to_send)
                    self.statistics[STATISTIC_MESSAGE_SENT_PARAMETER] += 1
            except Exception as e:
                log.exception(e)

    # def connect_test_for_pymcprotocol(self):
    #     pymc3e = Type3E()
    #     # If you use ascii byte communication, (Default is "binary")
    #     pymc3e.setaccessopt(commtype="binary")
    #     pymc3e.connect("192.168.3.39", 6000)
    #     wordunits_values = pymc3e.batchread_wordunits(headdevice="D100", readsize=10)
    #     print(wordunits_values)
