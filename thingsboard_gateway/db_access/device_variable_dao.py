from thingsboard_gateway.db_access.dao_base import DaoBase
from thingsboard_gateway.db_access.sqlitedao import SqliteDao
import thingsboard_gateway.gateway.global_var as global_var


class DeviceVariableDao(DaoBase):
    def __init__(self):
        super().__init__("device_variable")

    def get_all(self):
        return self.dao.search_table(self.table_name, {})

    def get_one_by_var_id(self, variable_id):
        return self.dao.search_table(self.table_name, {"id": variable_id})

    def get_one(self, device_name, tag_name):
        sql = "SELECT t3.device_id as deviceId, t3.tag_name as tag,t3.tag_type as type, t3.function_code as functionCode,t3.count as objectsCount,t3.address " \
              "FROM connector t1, device t2,device_variable t3 where t1.id = t2.connector_type and t2.id = t3.device_id and t3.tag_name = {} and t2.device_name = {}"\
            .format('"'+tag_name+'"', '"'+device_name+'"')
        result = self.dao.fetch(sql)
        if result:
            return result[0]
        else:
            return []

    def get_device_id(self, variable_id):
        result = self.dao.search_table(self.table_name, {"id": variable_id})
        if result:
            return result[0]["device_id"]
        else:
            return None

    def get_all_by_device_name(self, device_name):
        return self.dao.search_table(self.table_name, {"device_name": device_name})

    def update_variable_value(self, device_id, var_list):
        if var_list:
            conditions = [{"device_id": device_id, "tag_name": list(item.keys())[0]} for item in var_list]
            values = [{"value": str(list(item.values())[0])} for item in var_list]
            self.dao.update_many(self.table_name, values, conditions)

    def update_variable_parameter(self):
        pass

    def load_variable_parameter(self):
        return self.dao.search_table(self.table_name, {})

    def get_count_by_name(self, device_name):
        if device_name is not None:
            sql = "select count(*) from {} where device_name = {}".format(self.table_name, '"' + device_name + '"')
            result = self.dao.fetch(sql)
            return result[0]['count(*)']
        else:
            sql = "select count(*) from {}".format(self.table_name)
            result = self.dao.fetch(sql)
            return result[0]['count(*)']

    def get_count_by_devId(self, idDev):
        if id is not None:
            sql = "select count(*) from {} where device_id = {}".format(self.table_name, idDev)
            result = self.dao.fetch(sql)
            return result[0]['count(*)']
        else:
            sql = "select count(*) from {}".format(self.table_name)
            result = self.dao.fetch(sql)
            return result[0]['count(*)']

    def selectAllFromDeviceVariable(self, id, sqlStartIndex, sqlNumber, sortField, sortType):
        sql = "select * from {} where 1=1".format(self.table_name)
        if id is not None:
            sql += " and device_id ={}".format(id)
        if sortField is not None and len(sortField) != 0:
            sql += " order by {}".format(sortField)
        if sortType is not None and len(sortType) != 0:
            sql += " {}".format(sortType)
        if sqlStartIndex is not None:
            sql += " limit {}".format(sqlStartIndex)
        if sqlNumber is not None:
            sql += ",{}".format(sqlNumber)
        return self.dao.fetch(sql)

    def delete(self, id):
        return self.dao.delete_rows(self.table_name, {"id": id})

    def deleteName(self, deviceName):
        return self.dao.delete_rows(self.table_name, {"device_name": deviceName})

    def update(self, devVariable):
        self.dao.update_con(self.table_name, devVariable, {"id": devVariable['id']})
        return 1