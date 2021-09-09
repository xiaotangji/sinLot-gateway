from thingsboard_gateway.db_access.dao_base import DaoBase


class UserDao(DaoBase):
    def __init__(self):
        super().__init__("user")

    def get_one(self, name):
        return self.dao.search_table(self.table_name, {'name': name})

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def selectAllFromUser(self, sqlStartIndex, sqlNumber, sortField, sortType):
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

    def update(self, user):
        self.dao.update_rows(self.table_name, user, {"user_name": user['user_name']})
        return 1

    def delete(self, user_name):
        return self.dao.delete_rows(self.table_name, {"user_name": user_name})

    def selectFromUserByUserNameAndPassword(self, user_name, password):
        sql = "select * from {} where 1=1".format(self.table_name)
        sql += " and user_name = {}".format('"'+user_name+'"')
        sql += " and password = {}".format('"'+password+'"')
        return self.dao.fetch(sql)
