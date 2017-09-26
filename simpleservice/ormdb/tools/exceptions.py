from simpleservice.ormdb.exceptions import DBError


class DBExist(DBError):
    def __init__(self, schema):
        self.message = "Database %s already exist" % schema

class DBNotExist(DBError):
    def __init__(self, schema):
        self.message = "Database %s is not exist" % schema


class DropCreatedDBFail(DBError):
    def __init__(self, message, url):
        self.message = message
        self.url = url


class CopyRowOverSize(DBError):
    def __init__(self, message):
        self.message = message
