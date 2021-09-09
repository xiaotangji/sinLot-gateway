from thingsboard_gateway.db_access.dao_base import DaoBase
from thingsboard_gateway.db_access.sqlitedao import SqliteDao
import thingsboard_gateway.gateway.global_var as global_var


class RoutingStaticDao(DaoBase):
    def __init__(self):
        super().__init__("routing_static")

    def get_one(self, name):
        return self.dao.search_table(self.table_name, {'name': name})

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def selectFromRoutingStatic(self, sqlStartIndex, sqlNumber, sortField, sortType):
        sql = "select * from {} where 1=1".format(self.table_name)
        if sortField is not None and len(sortField) != 0:
            sql += " order by {}".format(sortField)
        if sortType is not None and len(sortType) != 0:
            sql += " {}".format(sortType)
        if sqlStartIndex is not None:
            sql += " limit {}".format(sqlStartIndex)
        if sqlNumber is not None:
            sql += ",{}".format(sqlNumber)
        return self.dao.fetch(sql)

    def selectCountFromRoutingStatic(self):
        sql = "select count(*) from {}".format(self.table_name)
        result = self.dao.fetch(sql)
        return result[0]['count(*)']

    def update(self, routingStatic):
        self.dao.update_rows(self.table_name, routingStatic, {"id": routingStatic['id']})
        return 1

    def delete(self, id):
        return self.dao.delete_rows(self.table_name, {"id": id})
