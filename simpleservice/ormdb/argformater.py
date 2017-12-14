import os
import six
import time
import re
import sqlalchemy
import sqlalchemy.event

import eventlet
from eventlet import hubs

from sqlalchemy import pool
from sqlalchemy import exc

from simpleutil.log import log as logging
from simpleutil.config import cfg

from simpleservice.ormdb import utils
from simpleservice.ormdb import exceptions
from simpleservice.ormdb.config import database_opts


LOG = logging.getLogger(__name__)


def cancel_execute(gleent):
    if gleent.dead:
        return
    LOG.warning('Cursor Execute Over Time')
    gleent.throw(exceptions.DBExecuteTimeOut('Cursor Execute Over Time'))


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
        os.path.dirname(sys.modules['simpleservice.ormdb'].__file__),
        os.path.dirname(sys.modules['sqlalchemy'].__file__)
    ])
    try:
        skip_paths = set([
            os.path.dirname(sys.modules['simpleservice.ormdb.tools'].__file__),
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
    if not engine_args['connect_args'].get('charset'):
        if 'charset' not in url.query:
            engine_args['connect_args']['charset'] = 'utf8'


@init_connection_args.dispatch_for("mysql+mysqlconnector")
def init_connection_args(url, engine_args, **kw):
    # mysqlconnector engine (<1.0) incorrectly defaults to
    # raise_on_warnings=True
    #  https://bitbucket.org/zzzeek/sqlalchemy/issue/2515
    if 'raise_on_warnings' not in url.query:
        engine_args['connect_args']['raise_on_warnings'] = True


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


@init_connection_args.dispatch_for("sqlite")
def _init_connection_args(url, engine_args, **kw):
    pool_class = url.get_dialect().get_pool_class(url)
    # singletonthreadpool is used for :memory: connections;
    # replace it with StaticPool.
    if issubclass(pool_class, pool.SingletonThreadPool):
        engine_args["poolclass"] = pool.StaticPool
        engine_args['connect_args']['check_same_thread'] = False



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


@init_events.dispatch_for("mysql+mysqlconnector")
def init_events(engine, **kw):
    """python mysql driver can use eventlet to cancel on executeing"""
    @sqlalchemy.event.listens_for(engine, "before_cursor_execute")
    def execute_timeout_task(conn, cursor, statement,
                             parameters, context, executemany):
        if cursor is None:
            return
        timer = None
        timeout = context.execution_options.get('timeout', None)
        if timeout and timeout > 0.0:
            hub = hubs.get_hub()
            timer = hub.schedule_call_global(timeout, cancel_execute, eventlet.getcurrent())
        setattr(cursor, 'timeout_task', timer)


    @sqlalchemy.event.listens_for(engine, "after_cursor_execute")
    def execute_nottimeout(conn, cursor, statement,
                             parameters, context, executemany):
        if cursor is None:
            return
        timer = getattr(cursor, 'timeout_task', None)
        if timer:
            timer.cancel()
            delattr(cursor, 'timeout_task')


    @sqlalchemy.event.listens_for(engine, "dbapi_error")
    def execute_error(conn, cursor, statement,
                      parameters, context, executemany):
        if cursor is None:
            return
        timer = getattr(cursor, 'timeout_task', None)
        if timer:
            timer.cancel()
            delattr(cursor, 'timeout_task')


@init_events.dispatch_for("sqlite")
def _init_events(engine, sqlite_synchronous=True, sqlite_fk=False, **kw):
    """Set up event listeners for SQLite.

    This includes several settings made on connections as they are
    created, as well as transactional control extensions.

    """

    def regexp(expr, item):
        reg = re.compile(expr)
        return reg.search(six.text_type(item)) is not None

    @sqlalchemy.event.listens_for(engine, "connect")
    def _sqlite_connect_events(dbapi_con, con_record):

        # Add REGEXP functionality on SQLite connections
        dbapi_con.create_function('regexp', 2, regexp)

        if not sqlite_synchronous:
            # Switch sqlite connections to non-synchronous mode
            dbapi_con.execute("PRAGMA synchronous = OFF")

        # Disable pysqlite's emitting of the BEGIN statement entirely.
        # Also stops it from emitting COMMIT before any DDL.
        # below, we emit BEGIN ourselves.
        # see http://docs.sqlalchemy.org/en/rel_0_9/dialects/\
        # sqlite.html#serializable-isolation-savepoints-transactional-ddl
        dbapi_con.isolation_level = None

        if sqlite_fk:
            # Ensures that the foreign key constraints are enforced in SQLite.
            dbapi_con.execute('pragma foreign_keys=ON')

    @sqlalchemy.event.listens_for(engine, "begin")
    def _sqlite_emit_begin(conn):
        # emit our own BEGIN, checking for existing
        # transactional state
        if 'in_transaction' not in conn.info:
            conn.execute("BEGIN")
            conn.info['in_transaction'] = True

    @sqlalchemy.event.listens_for(engine, "rollback")
    @sqlalchemy.event.listens_for(engine, "commit")
    def _sqlite_end_transaction(conn):
        # remove transactional marker
        conn.info.pop('in_transaction', None)


connformater = 'mysql+mysqlconnector://%(user)s:%(passwd)s@%(host)s:%(port)s/%(schema)s'
noschemaconn = 'mysql+mysqlconnector://%(user)s:%(passwd)s@%(host)s:%(port)s'


template = cfg.ConfigOpts()
template.register_opts(database_opts)
