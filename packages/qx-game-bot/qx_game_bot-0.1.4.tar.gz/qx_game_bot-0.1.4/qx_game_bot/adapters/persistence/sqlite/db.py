from peewee import SqliteDatabase

database = SqliteDatabase(None)


def initSqliteMemoryDatbase():
    database.init(":memory:")


def initSqliteFileDatabase(filepath: str = "app.db"):
    database.init(filepath)
