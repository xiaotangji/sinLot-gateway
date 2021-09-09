class GlobalVar:
    db_path = ''


def get_db_path():
    return GlobalVar.db_path


def set_db_path(path):
    GlobalVar.db_path = path