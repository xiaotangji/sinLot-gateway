from thingsboard_gateway.db_access.dao_base import DaoBase


class SystemDao(DaoBase):
    def __init__(self):
        super().__init__("collector")

    def selectToDayFromCollector(self, start, end):
        sql = "select memory,cpu,disk_io,network_io,record_time,cpu_temp,gpu_temp from {} where 1=1 and " \
              "record_time between {} and {}".format(self.table_name, '"' + start + '"', '"' + end + '"')
        result = self.dao.fetch(sql)
        if result is not None:
            return result
        else:
            return None
