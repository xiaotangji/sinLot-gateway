from thingsboard_gateway.db_access.dao_base import DaoBase
from thingsboard_gateway.db_access.sqlitedao import SqliteDao
import thingsboard_gateway.gateway.global_var as global_var


class StaticIpConfigDao(DaoBase):
    def __init__(self):
        super().__init__("static_ip_config")

    def get_one(self, name):
        return self.dao.search_table(self.table_name, {'name': name})

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def selectFromStaticIpConfig(self):
        sql = "select * from {}".format(self.table_name)
        return self.dao.fetch(sql)

    def update(self, staticIp):
        self.dao.update_rows(self.table_name, staticIp, {"id": staticIp['id']})
        return 1

    def delete(self, id):
        return self.dao.delete_rows(self.table_name, {"id": id})
