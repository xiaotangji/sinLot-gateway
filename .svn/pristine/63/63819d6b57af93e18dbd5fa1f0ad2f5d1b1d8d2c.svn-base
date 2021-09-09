import sqlite3

from sqlite3 import Error


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SqliteHelper:

    def __init__(self, file):
        self.__file = file
        self.__conn = None

    def connect(self):
        try:
            self.__conn = sqlite3.connect(self.__file)
            self.__conn.row_factory = dict_factory
            print("Connection is established: Sqlite Database is created ")
            return self.__conn
        except Error:
            print(Error)

    def execute(self, sql):
        cursorobj = self.__conn.cursor()
        cursorobj.execute(sql)
        self.__conn.commit()
        cursorobj.close()

    def fetch(self, sql):
        cursorobj = self.__conn.cursor()
        cursorobj.execute(sql)
        rows = cursorobj.fetchall()
        cursorobj.close()
        return rows

    def close(self):
        if self.__conn is not None:
            self.__conn.close()
