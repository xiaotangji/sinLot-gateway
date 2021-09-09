from thingsboard_gateway.db_access.dao_base import DaoBase


class MonitorDao(DaoBase):
    def __init__(self):
        super().__init__("monitor_setting")

    def update(self, monitor):
        self.dao.update_monitor(self.table_name, monitor)
        return 1

    def selectFromMonitor(self):
        sql = "select * from {}".format(self.table_name)
        result = self.dao.fetch(sql)
        if result is not None:
            return result[0]
        else:
            return None


