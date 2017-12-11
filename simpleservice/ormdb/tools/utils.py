import copy

from simpleutil.config import cfg

import sqlalchemy as sa
from sqlalchemy.pool import NullPool
from sqlalchemy.engine.url import make_url
from sqlalchemy.engine.base import Engine

from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import SQLAlchemyError

from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.argformater import connformater
from simpleservice.ormdb.exceptions import AcceptableError
from simpleservice.ormdb.exceptions import DBError
from simpleservice.ormdb.tools import exceptions


database_init_opts = [
    cfg.StrOpt('user',
               default='root',
               help='mysql database root user name'),
    cfg.StrOpt('passwd',
               default='',
               help='mysql database root password'),
    cfg.StrOpt('host',
               default='127.0.0.1',
               help='mysql host or ipaddress'),
    cfg.PortOpt('port',
                default=3306,
                help='mysql server post'),
    cfg.StrOpt('schema',
               required=True,
               help='target mysql database schema')
]


def get_no_schema_engine(engine):
    url = copy.copy(make_url(engine.url))
    url.database = None
    no_schema_engine = sa.create_engine(url, poolclass=NullPool)
    return no_schema_engine


# get schema info
def get_schema_info(engine):
    schema = engine.url.database
    no_schema_engine = get_no_schema_engine(engine)
    sql = "SELECT SCHEMA_NAME,DEFAULT_CHARACTER_SET_NAME,DEFAULT_COLLATION_NAME " \
          "FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'" % schema
    schema_info = no_schema_engine.execute(sql).fetchall()
    if schema_info:
        return schema_info[0]
    return None


# create a schema
def create_schema(engine, charcter_set=None, collation_type=None):

    schema = engine.url.database
    no_schema_engine = get_no_schema_engine(engine)
    if get_schema_info(engine):
        raise exceptions.DBExist(schema)
    if not charcter_set:
        charcter_set = 'utf8'
    sql = "CREATE DATABASE %s DEFAULT CHARACTER SET %s" % (schema, charcter_set)
    if collation_type:
        sql += ' COLLATE %s' % collation_type
    no_schema_engine.execute(sql)


# drop a schema
def drop_schema(engine):
    if get_schema_info(engine):
        sql = "DROP DATABASE %s" % engine.url.database
        engine.execute(sql)


def re_create_schema(engine):
    schema_info = get_schema_info(engine)
    if not schema_info:
        raise exceptions.DBNotExist(engine.url.database)
    drop_schema(engine)
    create_schema(engine, schema_info[1], schema_info[2])


create_databse = create_schema
drop_databse = drop_schema
re_create_database = re_create_schema


def init_database(db_info, metadata,
                  charcter_set=None,
                  collation_type=None,
                  init_data_func=None):
    if isinstance(db_info, Engine):
        engine = db_info
    else:
        database_connection = db_info
        if isinstance(db_info, dict):
            database_connection = connformater % db_info
        engine = create_engine(database_connection, thread_checkin=False,
                               poolclass=NullPool)
    try:
        create_schema(engine, charcter_set, collation_type)
    except OperationalError as e:
        raise AcceptableError('Create distribution database error:%d, %s' %
                              (e.orig[0], e.orig[1].replace("'", '')))
    except exceptions.DBExist as e:
        raise AcceptableError('Create distribution database error: %s' % e.message)
    try:
        metadata.create_all(bind=engine)
        if init_data_func:
            init_data_func(engine)
    except (OperationalError, SQLAlchemyError, DBError, Exception) as e:
        try:
            drop_schema(engine)
        except Exception:
            raise exceptions.DropCreatedDBFail('Create table fail, Drop database fail', str(engine.url))
        if isinstance(e, OperationalError):
            raise AcceptableError('Create table error:%d, %s' %
                                  (e.orig[0], e.orig[1].replace("'", '')))
        raise AcceptableError('Create tables or insert row error: %s' % e.message)

