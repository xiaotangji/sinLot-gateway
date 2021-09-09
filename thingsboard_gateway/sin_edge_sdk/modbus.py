from base_request import BaseRequest


class ModbusComm(BaseRequest):

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRequest.__init__(self, ip=ip, port=port)
        else:
            BaseRequest.__init__(self)
        self.read_tag_url = self.url_base + '/gateway/edge/readSingleTag'
        self.write_tag_url = self.url_base + '/gateway/edge/writeSingleTag'

    def read_tag(self, tag):
        return self.post_url_info(self.read_tag_url, tag)

    def write_tag(self, tag):
        return self.post_url_info(self.write_tag_url, tag)


if __name__ == '__main__':
    modbus = ModbusComm("127.0.0.1", "8078")
    write_tag = {"data": {"tag": "32int_read", "type": "integer", "functionCode": 6, "objectsCount": 1, "address": 6,
                    "deviceName": "modbus3_sensor", "payload": 21, "registered": False}}
    response = modbus.write_tag(write_tag)
    print('write_tag: %s' % response)

    read_tag = {"data":{"tag":"8int_read","type":"integer","functionCode":3,"objectsCount":1,"address":6, "deviceName":"modbus3_sensor","registered":False}}
    response = modbus.read_tag(read_tag)
    print('read_tag: %s' % response)
