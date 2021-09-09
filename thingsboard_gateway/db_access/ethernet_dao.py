from thingsboard_gateway.db_access.dao_base import DaoBase
from thingsboard_gateway.db_access.sqlitedao import SqliteDao
import thingsboard_gateway.gateway.global_var as global_var


class EthernetDao(DaoBase):
    def __init__(self):
        super().__init__("ethernet")

    def get_one(self, name):
        return self.dao.search_table(self.table_name, {'name': name})

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def update(self, ethernet):
        self.dao.update_row(self.table_name, ethernet, {"name": ethernet['name']})
        return 1

