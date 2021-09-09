from thingsboard_gateway.db_access.dao_base import DaoBase
from thingsboard_gateway.db_access.sqlitedao import SqliteDao
import thingsboard_gateway.gateway.global_var as global_var


class SlaveIpDao(DaoBase):
    def __init__(self):
        super().__init__("slave_ip_config")

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def update(self, ethernet):
        self.dao.update_row(self.table_name, ethernet, {"name": ethernet['name']})
        return 1

    def deleteSlave(self, id):
        return self.dao.delete_rows(self.table_name, {"id": id})