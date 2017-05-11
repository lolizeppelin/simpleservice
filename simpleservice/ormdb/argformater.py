import os
import six
import time
import sqlalchemy
import sqlalchemy.event

from sqlalchemy import pool
from sqlalchemy import exc

from simpleutil.log import log as logging
from simpleutil.config import cfg

from simpleservice.ormdb import utils
from simpleservice.ormdb.config import database_opts

LOG = logging.getLogger(__name__)


def _thread_yield(dbapi_con, con_record):
    """Ensure other greenthreads get a chance to be executed.

    If we use eventlet.monkey_patch(), eventlet.greenthread.sleep(0) will
    execute instead of time.sleep(0).
    Force a context switch. With common database backends (eg MySQLdb and
    sqlite), there is no implicit yield caused by network I/O since they are
    implemented by C libraries that eventlet cannot monkey patch.
    """
    time.sleep(0)


def _add_trace_comments(engine):
    """Add trace comments.

    Augment statements with a trace of the immediate calling code
    for a given statement.
    """
    import sys
    import traceback
    target_paths = set([
        os.path.dirname(sys.modules['oslo_db'].__file__),
        os.path.dirname(sys.modules['sqlalchemy'].__file__)
    ])
    try:
        skip_paths = set([
            os.path.dirname(sys.modules['oslo_db.tests'].__file__),
        ])
    except KeyError:
        skip_paths = set()

    @sqlalchemy.event.listens_for(engine, "before_cursor_execute", retval=True)
    def before_cursor_execute(conn, cursor, statement, parameters, context,
                              executemany):

        # NOTE(zzzeek) - if different steps per DB dialect are desirable
        # here, switch out on engine.name for now.
        stack = traceback.extract_stack()
        our_line = None

        for idx, (filename, line, method, function) in enumerate(stack):
            for tgt in skip_paths:
                if filename.startswith(tgt):
                    break
            else:
                for tgt in target_paths:
                    if filename.startswith(tgt):
                        our_line = idx
                        break
            if our_line:
                break

        if our_line:
            trace = "; ".join(
                "File: %s (%s) %s" % (
                    line[0], line[1], line[2]
                )
                # include three lines of context.
                for line in stack[our_line - 3:our_line]

            )
            statement = "%s  -- %s" % (statement, trace)

        return statement, parameters


def _add_process_guards(engine):
    """Add multiprocessing guards.

    Forces a connection to be reconnected if it is detected
    as having been shared to a sub-process.

    """
    @sqlalchemy.event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        connection_record.info['pid'] = os.getpid()

    @sqlalchemy.event.listens_for(engine, "checkout")
    def checkout(dbapi_connection, connection_record, connection_proxy):
        pid = os.getpid()
        if connection_record.info['pid'] != pid:
            LOG.debug(
                "Parent process %(orig)s forked (%(newproc)s) with an open "
                "database connection, "
                "which is being discarded and recreated.",
                {"newproc": pid, "orig": connection_record.info['pid']})
            connection_record.connection = connection_proxy.connection = None
            raise exc.DisconnectionError(
                "Connection record belongs to pid %s, "
                "attempting to check out in pid %s" %
                (connection_record.info['pid'], pid)
            )


@utils.dispatch_for_dialect('*', multiple=True)
def init_connection_args(url, engine_args,
                         max_pool_size=None, max_overflow=None, pool_timeout=None, **kw):

    pool_class = url.get_dialect().get_pool_class(url)
    if issubclass(pool_class, pool.QueuePool):
        if max_pool_size is not None:
            engine_args['pool_size'] = max_pool_size
        if max_overflow is not None:
            engine_args['max_overflow'] = max_overflow
        if pool_timeout is not None:
            engine_args['pool_timeout'] = pool_timeout


@init_connection_args.dispatch_for("mysql")
def init_connection_args(url, engine_args, **kw):
    if 'charset' not in url.query:
        engine_args['connect_args']['charset'] = 'utf8'


@init_connection_args.dispatch_for("mysql+mysqlconnector")
def init_connection_args(url, engine_args, **kw):
    # mysqlconnector engine (<1.0) incorrectly defaults to
    # raise_on_warnings=True
    #  https://bitbucket.org/zzzeek/sqlalchemy/issue/2515
    if 'raise_on_warnings' not in url.query:
        engine_args['connect_args']['raise_on_warnings'] = False


@init_connection_args.dispatch_for("mysql+mysqldb")
def init_connection_args(url, engine_args, **kw):
    # Those drivers require use_unicode=0 to avoid performance drop due
    # to internal usage of Python unicode objects in the driver
    #  http://docs.sqlalchemy.org/en/rel_0_9/dialects/mysql.html
    if 'use_unicode' not in url.query:
        if six.PY3:
            engine_args['connect_args']['use_unicode'] = 1
        else:
            engine_args['connect_args']['use_unicode'] = 0


@utils.dispatch_for_dialect('*', multiple=True)
def init_events(engine, thread_checkin=True, connection_trace=False, **kw):
    """Set up event listeners for all database backends."""

    _add_process_guards(engine)

    if connection_trace:
        _add_trace_comments(engine)

    if thread_checkin:
        sqlalchemy.event.listen(engine, 'checkin', _thread_yield)


@init_events.dispatch_for("mysql")
def init_events(engine, mysql_sql_mode=None, **kw):
    """Set up event listeners for MySQL."""

    if mysql_sql_mode is not None:
        @sqlalchemy.event.listens_for(engine, "connect")
        def _set_session_sql_mode(dbapi_con, connection_rec):
            cursor = dbapi_con.cursor()
            cursor.execute("SET SESSION sql_mode = %s", [mysql_sql_mode])

    @sqlalchemy.event.listens_for(engine, "first_connect")
    def _check_effective_sql_mode(dbapi_con, connection_rec):
        if mysql_sql_mode is not None:
            _set_session_sql_mode(dbapi_con, connection_rec)

        cursor = dbapi_con.cursor()
        cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
        realmode = cursor.fetchone()

        if realmode is None:
            LOG.warning('Unable to detect effective SQL mode')
        else:
            realmode = realmode[1]
            LOG.debug('MySQL server mode set to %s', realmode)
            if 'TRADITIONAL' not in realmode.upper() and \
                'STRICT_ALL_TABLES' not in realmode.upper():
                LOG.warning(
                        "MySQL SQL mode is '%s', "
                        "consider enabling TRADITIONAL or STRICT_ALL_TABLES",
                    realmode)


connformater = 'mysql://%(user)s:%(passwd)s@%(host)s:%(port)s/%(schema)s'


template = cfg.ConfigOpts()
template.register_opts(database_opts)
