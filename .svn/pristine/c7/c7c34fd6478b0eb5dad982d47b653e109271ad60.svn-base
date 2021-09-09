

from thingsboard_gateway.db_access.dao_base import DaoBase


class ConnectorDao(DaoBase):
    def __init__(self):
        super().__init__("connector")

    def get_one(self, connector_name):
        return self.dao.search_table(self.table_name, {'name': connector_name})

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def get_count_by_name(self, connector_name):
        if connector_name != '':
            sql = "select count(*) from {} where name = {}".format(self.table_name, '"' + connector_name + '"')
            result = self.dao.fetch(sql)
            return result[0]['count(*)']
        else:
            sql = "select count(*) from {}".format(self.table_name)
            result = self.dao.fetch(sql)
            return result[0]['count(*)']

    def selectAllFromCon(self, conName, sqlStartIndex, sqlNumber, sortField, sortType):
        sql = "select * from {} where 1=1".format(self.table_name)
        if conName is not None and len(conName) != 0:
            sql += " and name={}".format('"' + conName + '"')
        if sortField is not None and len(sortField) != 0:
            sql += " order by {}".format(sortField)
        if sortType is not None and len(sortType) != 0:
            sql += " {}".format(sortType)
        if sqlStartIndex is not None:
            sql += " limit {}".format(sqlStartIndex)
        if sqlNumber is not None:
            sql += ",{}".format(sqlNumber)
        return self.dao.fetch(sql)

    # def insert(self, data):
    #     return self.__dao.insert_row(self.__table_name, data)

    def selectIdFromConByConName(self, connector_name):
        sql = "select id from {} where name = {} ".format(self.table_name, '"' + connector_name + '"')
        result = self.dao.fetch(sql)
        if result:
            return result[0]["id"]
        else:
            return None

    def update(self, connector):
        self.dao.update_con(self.table_name, connector, {"name": connector['name']})
        return 1

    def delete(self, con_name):
        return self.dao.delete_rows(self.table_name, {"name": con_name})
