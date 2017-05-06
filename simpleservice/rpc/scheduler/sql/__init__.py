import sqlalchemy
from sqlalchemy import sql

class TaskMarket(object):

    task_id = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)
    request_id = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    marker = sqlalchemy.Column(sqlalchemy.String(64), nullable=False)
    active = sqlalchemy.Column(sqlalchemy.Boolean,
                               server_default=sql.false(),
                               nullable=False)
    activetime = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    expiretime = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    def __init__(self):
        pass


    def __tablename__(cls):
        return cls.__name__.lower() + 's'