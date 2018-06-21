#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from simpleutil.config import cfg


database_opts = [
    cfg.StrOpt('connection',
               help='The SQLAlchemy connection string to use to connect to '
                    'the database.',
               secret=True),
    cfg.StrOpt('slave_connection',
               secret=True,
               help='The SQLAlchemy connection string to use to connect to the'
                    ' slave database.'),
    cfg.BoolOpt('debug',
                default=False,
                help='Record raw sql to log(set echo of SQLAlchemy to true)'),
    cfg.StrOpt('mysql_sql_mode',
               default='TRADITIONAL',
               help='The SQL mode to be used for MySQL sessions. '
                    'This option, including the default, overrides any '
                    'server-set SQL mode. To use whatever SQL mode '
                    'is set by the server configuration, '
                    'set this to no value. Example: mysql_sql_mode='),
    cfg.IntOpt('idle_timeout',
               default=600,
               help='Timeout before idle SQL connections are reaped.'),
    cfg.IntOpt('min_pool_size',
               default=1,
               help='Minimum number of SQL connections to keep open in a '
                    'pool.'),
    cfg.IntOpt('max_pool_size',
               default=5,
               help='Maximum number of SQL connections to keep open in a '
                    'pool.'),
    cfg.IntOpt('max_retries',
               default=10,
               help='Maximum number of database connection retries '
                    'during startup. Set to -1 to specify an infinite '
                    'retry count.'),
    cfg.IntOpt('retry_interval',
               default=10,
               help='Interval between retries of opening a SQL connection.'),
    cfg.IntOpt('max_overflow',
               default=30,
               help='If set, use this value for max_overflow with '
                    'SQLAlchemy.'),
    cfg.BoolOpt('connection_trace',
                default=False,
                help='Add Python stack traces to SQL as comment strings.'),
    cfg.IntOpt('pool_timeout',
               help='If set, use this value for pool_timeout with '
                    'SQLAlchemy.'),
    cfg.BoolOpt('use_db_reconnect',
                default=False,
                help='Enable the experimental use of database reconnect '
                     'on connection lost.'),
    cfg.IntOpt('db_retry_interval',
               default=1,
               help='Seconds between retries of a database transaction.'),
    cfg.BoolOpt('db_inc_retry_interval',
                default=True,
                help='If True, increases the interval between retries '
                     'of a database operation up to db_max_retry_interval.'),
    cfg.IntOpt('db_max_retry_interval',
               default=10,
               help='If db_inc_retry_interval is set, the '
                    'maximum seconds between retries of a '
                    'database operation.'),
    cfg.IntOpt('db_max_retries',
               default=20,
               help='Maximum retries in case of connection error or deadlock '
                    'error before error is '
                    'raised. Set to -1 to specify an infinite retry '
                    'count.'),
]
