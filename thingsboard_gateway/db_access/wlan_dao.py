from thingsboard_gateway.db_access.dao_base import DaoBase
from thingsboard_gateway.db_access.sqlitedao import SqliteDao
import thingsboard_gateway.gateway.global_var as global_var


class WlanDao(DaoBase):
    def __init__(self):
        super().__init__("wlan_config")

    def get_one(self, name):
        return self.dao.search_table(self.table_name, {'name': name})

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def selectFromWlanConfig(self):
        sql = "select * from {}".format(self.table_name)
        return self.dao.fetch(sql)

    def update(self, wlan):
        self.dao.update_rows(self.table_name, wlan, {"id": wlan['id']})
        return 1
