import copy
import contextlib

import sqlalchemy as sa
from sqlalchemy.pool import NullPool
from sqlalchemy.engine.url import make_url
from sqlalchemy.engine.base import Engine

from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import DatabaseError

from simpleutil.utils import jsonutils
from simpleutil.log import log as logging

from simpleservice.ormdb import orm
from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.argformater import connformater
from simpleservice.ormdb.exceptions import AcceptableError
from simpleservice.ormdb.exceptions import DBError
from simpleservice.ormdb.tools import exceptions

LOG = logging.getLogger(__name__)


AUTHSCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'required': ['user', 'passwd'],
        'properties': {'user': {'type': 'string'},
                       'passwd': {'type': 'string'},
                       'privileges': {'type': 'string'},
                       'source': {'type': 'string'}}
    }
}


def get_no_schema_engine(engine, **kwargs):
    url = copy.copy(make_url(engine.url))
    url.database = None
    no_schema_engine = sa.create_engine(url, poolclass=NullPool, connect_args=kwargs)
    return no_schema_engine


# get schema info
def get_schema_info(engine, **kwargs):
    schema = engine.url.database
    no_schema_engine = get_no_schema_engine(engine)
    sql = "SELECT SCHEMA_NAME,DEFAULT_CHARACTER_SET_NAME,DEFAULT_COLLATION_NAME " \
          "FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'" % schema
    schema_info = no_schema_engine.execute(sql).fetchall()
    if schema_info:
        return schema_info[0]
    return None


def create_privileges(engine, auths):
    jsonutils.schema_validate(auths, AUTHSCHEMA)
    schema = engine.url.database
    no_schema_engine = get_no_schema_engine(engine)
    sqls = []
    for auth in auths:
        _auth = {'schema': schema,
                 'user': auth.get('user'),
                 'passwd': auth.get('passwd'),
                 'source': auth.get('source') or '%',
                 'privileges': auth.get('privileges') or 'ALL'}
        sql = "GRANT %(privileges)s ON %(schema)s.* TO '%(user)s'@'%(source)s' IDENTIFIED by '%(passwd)s'" % _auth
        sqls.append(sql)
    sqls.append('FLUSH PRIVILEGES')
    with no_schema_engine.connect() as conn:
        for sql in sqls:
            r = conn.execute(sql)
            r.close()

# drop privileges
def drop_privileges(engine, auths, raise_error=False):
    jsonutils.schema_validate(auths, AUTHSCHEMA)
    schema = engine.url.database
    no_schema_engine = get_no_schema_engine(engine)
    sqls = []
    for auth in auths:
        _auth = {'schema': schema,
                 'user': auth.get('user'),
                 'source': auth.get('source') or '%',
                 'privileges': auth.get('privileges') or 'ALL'}
        sql = "REVOKE %(privileges)s ON %(schema)s.* FROM '%(user)s'@'%(source)s'" % _auth
        sqls.append(sql)
        _auth.pop('privileges')
        _auth.pop('schema')
        sql = "drop user '%(user)s'@'%(source)s'" % _auth
        sqls.append(sql)
    sql = 'FLUSH PRIVILEGES'
    sqls.append(sql)
    with no_schema_engine.connect() as conn:
        for sql in sqls:
            try:
                r = conn.execute(sql)
                r.close()
            except DatabaseError as e:
                LOG.warning('Drop privileges sql [%s] catch programing error' % sql)
                if LOG.isEnabledFor(logging.DEBUG):
                    LOG.exception('Message %s, errno %d' % (e.msg, e.errno))
                if raise_error:
                    raise e
                continue

@contextlib.contextmanager
def privileges(engine, auths):
    if not auths:
        yield
    else:
        create_privileges(engine, auths)
        try:
            yield
        except Exception as e:
            try:
                drop_privileges(engine, auths, raise_error=True)
            except Exception:
                LOG.error('Exception after create privilege, drop privilege fail')
            raise e


# create a schema
def create_schema(engine, auths=None, character_set=None, collation_type=None, **kwargs):
    if auths:
        jsonutils.schema_validate(auths, AUTHSCHEMA)
    schema = engine.url.database
    no_schema_engine = get_no_schema_engine(engine, **kwargs)
    if get_schema_info(engine):
        raise exceptions.DBExist(schema)
    if not character_set:
        character_set = 'utf8'
    sql = "CREATE DATABASE %s DEFAULT CHARACTER SET %s" % (schema, character_set)
    if collation_type:
        sql += ' COLLATE %s' % collation_type
    with privileges(engine, auths):
        no_schema_engine.execute(sql)


# drop a schema
def drop_schema(engine, auths=None):
    if auths:
        jsonutils.schema_validate(auths, AUTHSCHEMA)
    if get_schema_info(engine):
        sql = "DROP DATABASE %s" % engine.url.database
        engine.execute(sql)
    if auths:
        drop_privileges(engine, auths, raise_error=False)


# drop and create schema
def re_create_schema(engine):
    schema_info = get_schema_info(engine)
    if not schema_info:
        raise exceptions.DBNotExist(engine.url.database)
    drop_schema(engine)
    create_schema(engine, character_set=schema_info[1], collation_type=schema_info[2])


create_databse = create_schema
drop_databse = drop_schema
re_create_database = re_create_schema


def init_database(db_info, metadata,
                  auths=None,
                  character_set=None,
                  collation_type=None,
                  init_data_func=None, **kwargs):
    character_set = character_set or 'utf8'
    if isinstance(db_info, Engine):
        engine = db_info
    else:
        database_connection = db_info
        if isinstance(db_info, dict):
            database_connection = connformater % db_info
        engine = create_engine(database_connection, thread_checkin=False,
                               poolclass=NullPool, **kwargs)
    try:
        create_schema(engine, auths, character_set, collation_type)
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


MAX_COPY_ROW = 100000


def copydb(src, dst, auths=None, tables_need_copy=None, exec_sqls=None, **kwargs):
    """copy database from src to dst
    tables_need_copy include table that need copy data
    exec_sqls include list of sql should be run after copy"""
    metadata = sa.MetaData()
    src_connection = connformater % src
    dst_connection = connformater % dst
    src_engine = create_engine(src_connection, thread_checkin=False,
                               poolclass=NullPool, **kwargs)
    dst_engine = create_engine(dst_connection, thread_checkin=False,
                               poolclass=NullPool, **kwargs)
    try:
        schema_info = get_schema_info(src_engine)
        if not schema_info:
            raise AcceptableError('Get source database error: %s not exist' % src_engine.url.database)
        metadata.reflect(bind=src_engine)
    except OperationalError as e:
        raise AcceptableError('Get source database info or Reflect source database error:%d, %s' %
                              (e.orig[0], e.orig[1].replace("'", '')))

    def init_data(*args, **kwargs):
        if not tables_need_copy and not exec_sqls:
            return
        dst_session = orm.get_maker(dst_engine)()
        src_session = orm.get_maker(src_engine)()
        if tables_need_copy:
            count = 0
            for table in tables_need_copy:
                if table not in metadata.tables:
                    raise AcceptableError('Table %s not in source database' % table)
            for table_name in tables_need_copy:
                table = metadata.tables[table_name]
                # get row count from table
                count += src_session.query(sa.func.count("*")).select_from(table).scalar()
                if count >= MAX_COPY_ROW:
                    raise exceptions.CopyRowOverSize('Copy from table %s fail, too many rows copyed' %
                                                     table_name)
                # build a query in src database
                query = src_session.query(table)
                with dst_session.begin():
                    for row in query:
                        # execute insert sql on dst databases
                        dst_session.execute(table.insert(row))
        if exec_sqls:
            with dst_session.begin():
                for sql in exec_sqls:
                    dst_session.execute(sql)
        src_session.close()
        dst_session.close()

    init_database(dst_engine, metadata, auths,
                  character_set=schema_info[1],
                  collation_type=schema_info[2],
                  init_data_func=init_data)
    return schema_info