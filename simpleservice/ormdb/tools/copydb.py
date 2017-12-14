from sqlalchemy import MetaData
from sqlalchemy import func
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError

from simpleservice.ormdb import orm
from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.argformater import connformater
from simpleservice.ormdb.exceptions import AcceptableError

from simpleservice.ormdb.tools import exceptions
from simpleservice.ormdb.tools.utils import get_schema_info
from simpleservice.ormdb.tools.utils import init_database


MAX_COPY_ROW = 100000


def copydb(src, dst, auths=None, tables_need_copy=None, exec_sqls=None):
    """copy database from src to dst
    tables_need_copy include table that need copy data
    exec_sqls include list of sql should be run after copy"""
    metadata = MetaData()
    src_connection = connformater % src
    dst_connection = connformater % dst
    src_engine = create_engine(src_connection, thread_checkin=False,
                               poolclass=NullPool)
    dst_engine = create_engine(dst_connection, thread_checkin=False,
                               poolclass=NullPool)
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
                count += src_session.query(func.count("*")).select_from(table).scalar()
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

    try:
        init_database(dst_engine, metadata, auths,
                      charcter_set=schema_info[1],
                      collation_type=schema_info[2],
                      init_data_func=init_data)
    finally:
        del src_engine
        del dst_engine
