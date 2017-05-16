import copy

import sqlalchemy as sa
from sqlalchemy.pool import NullPool
from sqlalchemy.engine.url import make_url

from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import SQLAlchemyError

from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.argformater import connformater
from simpleservice.ormdb.exceptions import AcceptableError
from simpleservice.ormdb.exceptions import DBError
from simpleservice.ormdb.tools import exceptions


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
def create_schema(engine, charcter_set='utf8', collation_type=None):

    schema = engine.url.database
    no_schema_engine = get_no_schema_engine(engine)
    if get_schema_info(engine):
        raise exceptions.DBExist(schema)
    sql = "CREATE DATABASE %s DEFAULT CHARACTER SET %s" % (schema, charcter_set)
    if collation_type:
        sql += ' COLLATE %s' % collation_type
    no_schema_engine.execute(sql)


# drop a schema
def drop_schema(engine):
    if get_schema_info(engine):
        sql = "DROP DATABASE %s" % engine.url.database
        engine.execute(sql)


create_databse = create_schema
drop_databse = drop_schema


def init_manager_database(db_info, declarative_meta):
    manager_connection = connformater % db_info
    engine = create_engine(manager_connection, thread_checkin=False,
                           max_retries=0)
    try:
        create_schema(engine)
    except OperationalError as e:
        raise AcceptableError('Create distribution database error:%d, %s' %
                              (e.orig[0], e.orig[1].replace("'", '')))
    except exceptions.DBExist as e:
        raise AcceptableError('Create distribution database error: %s' % e.message)
    try:
        declarative_meta.metadata.create_all(bind=engine)
    except (OperationalError, DBError, SQLAlchemyError) as e:
        try:
            drop_schema(engine)
        except Exception:
            raise exceptions.DropCreateedDBFail('Create table fail, Drop database fail', manager_connection)
        if isinstance(e, OperationalError):
            raise AcceptableError('Create table error:%d, %s' %
                                  (e.orig[0], e.orig[1].replace("'", '')))
        raise AcceptableError('Create tables error: %s' % e.message)
