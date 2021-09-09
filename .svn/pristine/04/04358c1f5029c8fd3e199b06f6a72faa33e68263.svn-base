from thingsboard_gateway.db_access.dao_base import DaoBase


class TopicDao(DaoBase):
    def __init__(self):
        super().__init__("topic")

    def selectAllFromTopic(self, sqlStartIndex, sqlNumber, sortField, sortType):
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

    def delete(self, topicName):
        return self.dao.delete_rows(self.table_name, {"topicFilter": topicName})

    def update(self, topic):
        self.dao.update_row(self.table_name, topic, {"topicFilter": topic['topicFilter']})
        return 1