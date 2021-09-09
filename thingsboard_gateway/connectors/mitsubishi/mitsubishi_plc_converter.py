from thingsboard_gateway.connectors.converter import Converter, abstractmethod, log


class MPlcConverter(Converter):
    @abstractmethod
    def convert(self, config, data):
        pass
