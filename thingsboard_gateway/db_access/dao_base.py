import json

from thingsboard_gateway.db_access.sqlitedao import SqliteDao, SearchDict
import thingsboard_gateway.gateway.global_var as global_var


class DaoBase(object):
    def __init__(self, table_name):
        self.table_name = table_name
        if global_var.get_db_path() is not None and global_var.get_db_path().strip():
            self.dao = SqliteDao.get_instance(global_var.get_db_path())
            self.init_success = True
        else:
            self.init_success = False

    def re_init(self):
        if global_var.get_db_path() is not None or global_var.get_db_path().strip():
            self.dao = SqliteDao.get_instance(global_var.get_db_path())
            self.init_success = True
        else:
            self.init_success = False

    def get_count(self):
        sql = "select count(*) from {} ".format(self.table_name)
        result = self.dao.fetch(sql)
        return result[0]['count(*)']

    def get_countFromCon(self):
        sql = "select count(*) from {} ".format(self.table_name)
        result = self.dao.fetch(sql)
        return result[0]['count(*)']

    def insertDev(self, data):
        return self.dao.insert_row(self.table_name, data.get('device'))

    def insertCon(self, data):
        return self.dao.insert_row(self.table_name, data.get('connector'))

    def insertDevVariable(self, data):
        return self.dao.insert_row(self.table_name, json.loads(data))

    def insertTopic(self, data):
        return self.dao.insert_row(self.table_name, data.get('topic'))

    def insertEthernet(self, data):
        return self.dao.insert_row(self.table_name, data.get('ethernet'))

    def insertSlave(self, data):
        return self.dao.insert_row(self.table_name, data.get('slave'))

    def insertSsid(self, data):
        return self.dao.insert_row(self.table_name, data.get('ssid'))

    def insertDhcp(self, data):
        return self.dao.insert_row(self.table_name, data.get('dhcp'))

    def insertStaticIpConfig(self, data):
        return self.dao.insert_row(self.table_name, data.get('staticIp'))

    def insertRoutingStatic(self, data):
        return self.dao.insert_row(self.table_name, data.get('route'))

    def insertAccessControl(self, data):
        return self.dao.insert_row(self.table_name, data.get('access'))

    def insertUser(self, data):
        return self.dao.insert_row(self.table_name, data.get('user'))