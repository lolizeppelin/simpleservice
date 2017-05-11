from sqlalchemy import MetaData
from sqlalchemy.pool import NullPool

from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.argformater import connformater
from simpleservice.ormdb.exceptions import DBConnectionError

from sqlalchemy.exc import OperationalError

def copydb(src, dst, table_with_data=None, exec_sql=None):
    meta = MetaData()
    src_connection = connformater % src
    dst_connection = connformater % dst
    src_engine = create_engine(src_connection, thread_checkin=False,
                               poolclass=NullPool)
    dst_engine = create_engine(dst_connection, thread_checkin=False,
                               poolclass=NullPool)
    try:
        meta.reflect(bind=src_engine)
    except OperationalError, e:
        raise DBConnectionError('Reflect source database error:%d, %s' %
                                (e.orig[0], e.orig[1].replace("'", '')))
    try:
        meta.create_all(bind=dst_engine)
    except OperationalError, e:
        raise DBConnectionError('Create distribution database error:%d, %s' %
                                (e.orig[0], e.orig[1].replace("'", '')))
