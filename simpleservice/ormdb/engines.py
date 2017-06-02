# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""Core SQLAlchemy connectivity routines.
"""

import itertools
import time
import six

import logging as default_logging

import sqlalchemy
import sqlalchemy.engine.url
from sqlalchemy import event
from sqlalchemy.pool import NullPool

from sqlalchemy.sql.expression import select

from simpleutil.log import log as logging

from simpleservice.ormdb import exceptions
from simpleservice.ormdb import exc_filters
from simpleservice.ormdb.argformater import init_connection_args
from simpleservice.ormdb.argformater import init_events
from simpleservice.ormdb.argformater import template
from simpleservice.ormdb.argformater import connformater


LOG = logging.getLogger(__name__)


def _connect_ping_listener(connection, branch):
    """Ping the server at connection startup.

    Ping the server at transaction begin and transparently reconnect
    if a disconnect exception occurs.
    """
    if branch:
        return

    # turn off "close with result".  This can also be accomplished
    # by branching the connection, however just setting the flag is
    # more performant and also doesn't get involved with some
    # connection-invalidation awkardness that occurs (see
    # https://bitbucket.org/zzzeek/sqlalchemy/issue/3215/)
    save_should_close_with_result = connection.should_close_with_result
    connection.should_close_with_result = False
    try:
        # run a SELECT 1.   use a core select() so that
        # any details like that needed by Oracle, DB2 etc. are handled.
        connection.scalar(select([1]))
    except exceptions.DBConnectionError:
        # catch DBConnectionError, which is raised by the filter
        # system.
        # disconnect detected.  The connection is now
        # "invalid", but the pool should be ready to return
        # new connections assuming they are good now.
        # run the select again to re-validate the Connection.
        connection.scalar(select([1]))
    finally:
        connection.should_close_with_result = save_should_close_with_result


def _setup_logging(connection_debug=0):
    """setup_logging function maps SQL debug level to Python log level.

    Connection_debug is a verbosity of SQL debugging information.
    0=None(default value),
    1=Processed only messages with WARNING level or higher
    50=Processed only messages with INFO level or higher
    100=Processed only messages with DEBUG level
    """
    connection_trace = False
    if connection_debug >= 0:
        # logger = default_logging.getLogger('sqlalchemy.engine')
        if connection_debug >= 100:
            connection_trace = True
            LOG.setLevel(default_logging.DEBUG)
        elif connection_debug >= 50:
            LOG.setLevel(default_logging.INFO)
        else:
            LOG.setLevel(default_logging.WARNING)
    return connection_trace


def _test_connection(engine, max_retries, retry_interval):
    if max_retries == -1:
        attempts = itertools.count()
    else:
        attempts = six.moves.range(max_retries)
    # See: http://legacy.python.org/dev/peps/pep-3110/#semantic-changes for
    # why we are not using 'de' directly (it can be removed from the local
    # scope).
    de_ref = None
    for attempt in attempts:
        try:
            return engine.connect()
        except exceptions.DBConnectionError as de:
            msg = 'SQL connection failed. %s attempts left.'
            LOG.warning(msg, max_retries - attempt)
            time.sleep(retry_interval)
            de_ref = de
    else:
        if de_ref is not None:
            six.reraise(type(de_ref), de_ref)


def create_engine(sql_connection,
                  logging_name=None,
                  thread_checkin=True,
                  idle_timeout=None,
                  connection_debug=None,
                  max_pool_size=None,
                  max_overflow=None,
                  pool_timeout=None,
                  mysql_sql_mode=None,
                  max_retries=None,
                  retry_interval=None,
                  poolclass=None,
                  ):
    """Return a new SQLAlchemy engine."""

    if sql_connection is None:
        from simpleutil.common.exceptions import InvalidArgument
        raise InvalidArgument('sql_connection is None')
    if isinstance(sql_connection, dict):
        sql_connection = connformater % sql_connection

    # Set default value
    idle_timeout = idle_timeout if idle_timeout is not None else template.idle_timeout
    connection_debug = connection_debug if connection_debug is not None else template.connection_debug
    max_pool_size = max_pool_size if max_pool_size is not None else template.max_pool_size
    max_overflow = max_overflow if max_overflow is not None else template.max_overflow
    pool_timeout = pool_timeout if pool_timeout is not None else template.pool_timeout
    mysql_sql_mode = mysql_sql_mode if mysql_sql_mode is not None else template.mysql_sql_mode
    max_retries = max_retries if max_retries is not None else template.max_retries
    retry_interval = retry_interval if retry_interval is not None else template.retry_interval

    url = sqlalchemy.engine.url.make_url(sql_connection)

    engine_args = {
        "pool_recycle": idle_timeout,
        'convert_unicode': True,
        'connect_args': {},
        'logging_name': logging_name
    }
    if poolclass:
        engine_args.update({'poolclass': poolclass})
        if poolclass is NullPool:
            max_pool_size = None
            max_overflow = None
            pool_timeout = None
            max_retries = None

    init_connection_args(
        url, engine_args,
        max_pool_size=max_pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout
    )
    engine = sqlalchemy.create_engine(url, **engine_args)

    connection_trace = _setup_logging(connection_debug)
    init_events(
        engine,
        mysql_sql_mode=mysql_sql_mode,
        thread_checkin=thread_checkin,
        connection_trace=connection_trace
    )

    exc_filters.register_engine(engine)
    event.listen(engine, "engine_connect", _connect_ping_listener)

    if max_retries:
        test_conn = _test_connection(engine, max_retries, retry_interval)
        test_conn.close()
    return engine
