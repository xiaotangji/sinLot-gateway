from thingsboard_gateway.connectors.mitsubishi.mitsubishi_plc_converter import MPlcConverter, log


class BytesMPlcUplinkConverter(MPlcConverter):
    def __init__(self, config):
        self.__datatypes = {
            "timeseries": "telemetry",
            "attributes": "attributes"
        }
        self.__result = {"deviceName": config.get("deviceName", "ModbusDevice %s" % (str(config["unitId"]))),
                         "deviceType": config.get("deviceType", "default")}

    def convert(self, config, data):
        self.__result["telemetry"] = []
        self.__result["attributes"] = []
        for config_data in data:
            for tag in data[config_data]:
                try:
                    configuration = data[config_data][tag]["data_sent"]
                    response = data[config_data][tag]["input_data"]
                    decoded_data = None
                    if response.IsSuccess:
                        result = response.Content
                        log.debug(result)
                        decoded_data = result

                        if config_data == "rpc":
                            return decoded_data

                        if isinstance(decoded_data, list):
                            if configuration.get("divider"):
                                decoded_data = [float(__data) / float(configuration["divider"]) for __data in decoded_data]
                            if configuration.get("multiplier"):
                                decoded_data = [__data * configuration["multiplier"] for __data in decoded_data]
                        else:
                            if configuration.get("divider"):
                                decoded_data = float(decoded_data) / float(configuration["divider"])
                            if configuration.get("multiplier"):
                                decoded_data = decoded_data * configuration["multiplier"]
                    else:
                        log.debug("failed   " + response.Messageresponse)

                    log.debug("datatype: %s \t key: %s \t value: %s", self.__datatypes[config_data], tag, str(decoded_data))
                    self.__result[self.__datatypes[config_data]].append({tag: decoded_data})
                except Exception as e:
                    log.exception(e)
        log.debug(self.__result)
        return self.__result
