from sqlalchemy import MetaData
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError

from simpleservice.ormdb.engines import create_engine
from simpleservice.ormdb.argformater import connformater
from simpleservice.ormdb.exceptions import AcceptableError

from simpleservice.ormdb.tools.exceptions import DropCreateedDBFail
from simpleservice.ormdb.tools.exceptions import DBExist
from simpleservice.ormdb.tools.utils import get_schema_info
from simpleservice.ormdb.tools.utils import create_schema
from simpleservice.ormdb.tools.utils import drop_schema


def copydb(src, dst, table_with_data=None, exec_sql=None):
    meta = MetaData()
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
        meta.reflect(bind=src_engine)
    except OperationalError as e:
        raise AcceptableError('Get source database info or Reflect source database error:%d, %s' %
                              (e.orig[0], e.orig[1].replace("'", '')))
    try:
        create_schema(dst_engine, charcter_set=schema_info[1],
                      collation_type=schema_info[2])
    except OperationalError as e:
        raise AcceptableError('Create distribution database error:%d, %s' %
                              (e.orig[0], e.orig[1].replace("'", '')))
    except DBExist as e:
        raise AcceptableError('Create distribution database error: %s' % e.message)
    try:
        meta.create_all(bind=dst_engine)
    except OperationalError as e:
        try:
            drop_schema(dst_engine)
        except:
            raise DropCreateedDBFail('Copy table fail, Drop database fail', dst_connection)
        raise AcceptableError('Copy table into distribution database error:%d, %s'
                              % (e.orig[0], e.orig[1].replace("'", '')))
