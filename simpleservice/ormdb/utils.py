# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2010-2011 OpenStack Foundation.
# Copyright 2012 Justin Santa Barbara
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

import collections
import contextlib
import itertools
import logging
import re

from simpleutil.utils import timeutils
import six
import sqlalchemy
from sqlalchemy import Boolean
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy.engine import Connectable
from sqlalchemy.engine import reflection
from sqlalchemy.engine import url as sa_url
from sqlalchemy import func
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy.sql.expression import literal_column
from sqlalchemy.sql import text
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.types import NullType

from simpleservice.ormdb import exceptions

# NOTE(ochuprykov): Add references for backwards compatibility
InvalidSortKey = exceptions.InvalidSortKey
ColumnError = exceptions.ColumnError

LOG = logging.getLogger(__name__)

_DBURL_REGEX = re.compile(r"[^:]+://([^:]+):([^@]+)@.+")

_VALID_SORT_DIR = [
    "-".join(x) for x in itertools.product(["asc", "desc"],
                                           ["nullsfirst", "nullslast"])]


def sanitize_db_url(url):
    match = _DBURL_REGEX.match(url)
    if match:
        return '%s****:****%s' % (url[:match.start(1)], url[match.end(2):])
    return url


# copy from glance/db/sqlalchemy/api.py

def to_list(x, default=None):
    if x is None:
        return default
    if not isinstance(x, collections.Iterable) or \
            isinstance(x, six.string_types):
        return [x]
    elif isinstance(x, list):
        return x
    else:
        return list(x)


def _read_deleted_filter(query, db_model, deleted):
    if 'deleted' not in db_model.__table__.columns:
        raise ValueError("There is no `deleted` column in `%s` table. "
                         "Project doesn't use soft-deleted feature."
                         % db_model.__name__)

    default_deleted_value = db_model.__table__.c.deleted.default.arg
    if deleted:
        query = query.filter(db_model.deleted != default_deleted_value)
    else:
        query = query.filter(db_model.deleted == default_deleted_value)
    return query


def get_table(engine, name):
    """Returns an sqlalchemy table dynamically from db.

    Needed because the models don't work for us in migrations
    as models will be far out of sync with the current data.

    .. warning::

       Do not use this method when creating ForeignKeys in database migrations
       because sqlalchemy needs the same MetaData object to hold information
       about the parent table and the reference table in the ForeignKey. This
       method uses a unique MetaData object per table object so it won't work
       with ForeignKey creation.
    """
    metadata = MetaData()
    metadata.bind = engine
    return Table(name, metadata, autoload=True)


class InsertFromSelect(object):
    """Form the base for `INSERT INTO table (SELECT ... )` statement.

    DEPRECATED: this class is deprecated and will be removed from oslo_db
    in a few releases. Use default SQLAlchemy insert from select implementation
    instead

    :param table: table to insert records
    :param select: select query
    :param cols: list of columns to specify in insert clause
    :return: SQLAlchemy :class:`Insert` object instance

    Usage:

    .. code-block:: python

      select = sql.select(table_from)
      insert = InsertFromSelect(table_to, select,
                                ['id', 'name', 'insert_date'])
      engine.execute(insert)

    """
    # NOTE(tdurakov): Insert from select implementation added to SQLAlchemy
    # starting from version 0.8.7. Default SQLAlchemy implementation should be
    # used instead of this. Deprecated.

    def __new__(cls, table, select, cols=None):
        if not cols:
            cols = [c.name for c in table.c]

        return table.insert(inline=True).from_select(cols, select)

    def __init__(self, table, select, cols=None):
        pass


def _get_not_supported_column(col_name_col_instance, column_name):
    try:
        column = col_name_col_instance[column_name]
    except KeyError:
        msg = "Please specify column %s in col_name_col_instance param. " \
              "It is required because column has unsupported type by SQLite."
        raise exceptions.ColumnError(msg % column_name)

    if not isinstance(column, Column):
        msg = "col_name_col_instance param has wrong type of " \
              "column instance for column %s It should be instance " \
              "of sqlalchemy.Column."
        raise exceptions.ColumnError(msg % column_name)
    return column


def drop_old_duplicate_entries_from_table(migrate_engine, table_name,
                                          use_soft_delete, *uc_column_names):
    """Drop all old rows having the same values for columns in uc_columns.

    This method drop (or mark ad `deleted` if use_soft_delete is True) old
    duplicate rows form table with name `table_name`.

    :param migrate_engine:  Sqlalchemy engine
    :param table_name:      Table with duplicates
    :param use_soft_delete: If True - values will be marked as `deleted`,
                            if False - values will be removed from table
    :param uc_column_names: Unique constraint columns
    """
    meta = MetaData()
    meta.bind = migrate_engine

    table = Table(table_name, meta, autoload=True)
    columns_for_group_by = [table.c[name] for name in uc_column_names]

    columns_for_select = [func.max(table.c.id)]
    columns_for_select.extend(columns_for_group_by)

    duplicated_rows_select = sqlalchemy.sql.select(
        columns_for_select, group_by=columns_for_group_by,
        having=func.count(table.c.id) > 1)

    for row in migrate_engine.execute(duplicated_rows_select).fetchall():
        # NOTE(boris-42): Do not remove row that has the biggest ID.
        delete_condition = table.c.id != row[0]
        is_none = None  # workaround for pyflakes
        delete_condition &= table.c.deleted_at == is_none
        for name in uc_column_names:
            delete_condition &= table.c[name] == row[name]

        rows_to_delete_select = sqlalchemy.sql.select(
            [table.c.id]).where(delete_condition)
        for row in migrate_engine.execute(rows_to_delete_select).fetchall():
            LOG.info("Deleting duplicated row with id: %(id)s from table: "
                     "%(table)s", dict(id=row[0], table=table_name))

        if use_soft_delete:
            delete_statement = table.update().\
                where(delete_condition).\
                values({
                    'deleted': literal_column('id'),
                    'updated_at': literal_column('updated_at'),
                    'deleted_at': timeutils.utcnow()
                })
        else:
            delete_statement = table.delete().where(delete_condition)
        migrate_engine.execute(delete_statement)


def _get_default_deleted_value(table):
    if isinstance(table.c.id.type, Integer):
        return 0
    if isinstance(table.c.id.type, String):
        return ""
    raise exceptions.ColumnError("Unsupported id columns type")


def _restore_indexes_on_deleted_columns(migrate_engine, table_name, indexes):
    table = get_table(migrate_engine, table_name)

    insp = reflection.Inspector.from_engine(migrate_engine)
    real_indexes = insp.get_indexes(table_name)
    existing_index_names = dict(
        [(index['name'], index['column_names']) for index in real_indexes])

    # NOTE(boris-42): Restore indexes on `deleted` column
    for index in indexes:
        if 'deleted' not in index['column_names']:
            continue
        name = index['name']
        if name in existing_index_names:
            column_names = [table.c[c] for c in existing_index_names[name]]
            old_index = Index(name, *column_names, unique=index["unique"])
            old_index.drop(migrate_engine)

        column_names = [table.c[c] for c in index['column_names']]
        new_index = Index(index["name"], *column_names, unique=index["unique"])
        new_index.create(migrate_engine)


def change_deleted_column_type_to_boolean(migrate_engine, table_name,
                                          **col_name_col_instance):
    if migrate_engine.name == "sqlite":
        return _change_deleted_column_type_to_boolean_sqlite(
            migrate_engine, table_name, **col_name_col_instance)
    insp = reflection.Inspector.from_engine(migrate_engine)
    indexes = insp.get_indexes(table_name)

    table = get_table(migrate_engine, table_name)

    old_deleted = Column('old_deleted', Boolean, default=False)
    old_deleted.create(table, populate_default=False)

    table.update().\
        where(table.c.deleted == table.c.id).\
        values(old_deleted=True).\
        execute()

    table.c.deleted.drop()
    table.c.old_deleted.alter(name="deleted")

    _restore_indexes_on_deleted_columns(migrate_engine, table_name, indexes)


def _change_deleted_column_type_to_boolean_sqlite(migrate_engine, table_name,
                                                  **col_name_col_instance):
    insp = reflection.Inspector.from_engine(migrate_engine)
    table = get_table(migrate_engine, table_name)

    columns = []
    for column in table.columns:
        column_copy = None
        if column.name != "deleted":
            if isinstance(column.type, NullType):
                column_copy = _get_not_supported_column(col_name_col_instance,
                                                        column.name)
            else:
                column_copy = column.copy()
        else:
            column_copy = Column('deleted', Boolean, default=0)
        columns.append(column_copy)

    constraints = [constraint.copy() for constraint in table.constraints]

    meta = table.metadata
    new_table = Table(table_name + "__tmp__", meta,
                      *(columns + constraints))
    new_table.create()

    indexes = []
    for index in insp.get_indexes(table_name):
        column_names = [new_table.c[c] for c in index['column_names']]
        indexes.append(Index(index["name"], *column_names,
                             unique=index["unique"]))

    c_select = []
    for c in table.c:
        if c.name != "deleted":
            c_select.append(c)
        else:
            c_select.append(table.c.deleted == table.c.id)

    ins = InsertFromSelect(new_table, sqlalchemy.sql.select(c_select))
    migrate_engine.execute(ins)

    table.drop()
    for index in indexes:
        index.create(migrate_engine)

    new_table.rename(table_name)
    new_table.update().\
        where(new_table.c.deleted == new_table.c.id).\
        values(deleted=True).\
        execute()


def change_deleted_column_type_to_id_type(migrate_engine, table_name,
                                          **col_name_col_instance):
    if migrate_engine.name == "sqlite":
        return _change_deleted_column_type_to_id_type_sqlite(
            migrate_engine, table_name, **col_name_col_instance)
    insp = reflection.Inspector.from_engine(migrate_engine)
    indexes = insp.get_indexes(table_name)

    table = get_table(migrate_engine, table_name)

    new_deleted = Column('new_deleted', table.c.id.type,
                         default=_get_default_deleted_value(table))
    new_deleted.create(table, populate_default=True)

    deleted = True  # workaround for pyflakes
    table.update().\
        where(table.c.deleted == deleted).\
        values(new_deleted=table.c.id).\
        execute()
    table.c.deleted.drop()
    table.c.new_deleted.alter(name="deleted")

    _restore_indexes_on_deleted_columns(migrate_engine, table_name, indexes)


def _change_deleted_column_type_to_id_type_sqlite(migrate_engine, table_name,
                                                  **col_name_col_instance):
    # NOTE(boris-42): sqlaclhemy-migrate can't drop column with check
    #                 constraints in sqlite DB and our `deleted` column has
    #                 2 check constraints. So there is only one way to remove
    #                 these constraints:
    #                 1) Create new table with the same columns, constraints
    #                 and indexes. (except deleted column).
    #                 2) Copy all data from old to new table.
    #                 3) Drop old table.
    #                 4) Rename new table to old table name.
    insp = reflection.Inspector.from_engine(migrate_engine)
    meta = MetaData(bind=migrate_engine)
    table = Table(table_name, meta, autoload=True)
    default_deleted_value = _get_default_deleted_value(table)

    columns = []
    for column in table.columns:
        column_copy = None
        if column.name != "deleted":
            if isinstance(column.type, NullType):
                column_copy = _get_not_supported_column(col_name_col_instance,
                                                        column.name)
            else:
                column_copy = column.copy()
        else:
            column_copy = Column('deleted', table.c.id.type,
                                 default=default_deleted_value)
        columns.append(column_copy)

    def is_deleted_column_constraint(constraint):
        # NOTE(boris-42): There is no other way to check is CheckConstraint
        #                 associated with deleted column.
        if not isinstance(constraint, CheckConstraint):
            return False
        sqltext = str(constraint.sqltext)
        # NOTE(I159): in order to omit the CHECK constraint corresponding
        # to `deleted` column we have to test these patterns which may
        # vary depending on the SQLAlchemy version used.
        constraint_markers = (
            "deleted in (0, 1)",
            "deleted IN (:deleted_1, :deleted_2)",
            "deleted IN (:param_1, :param_2)"
        )
        return any(sqltext.endswith(marker) for marker in constraint_markers)

    constraints = []
    for constraint in table.constraints:
        if not is_deleted_column_constraint(constraint):
            constraints.append(constraint.copy())

    new_table = Table(table_name + "__tmp__", meta,
                      *(columns + constraints))
    new_table.create()

    indexes = []
    for index in insp.get_indexes(table_name):
        column_names = [new_table.c[c] for c in index['column_names']]
        indexes.append(Index(index["name"], *column_names,
                             unique=index["unique"]))

    ins = InsertFromSelect(new_table, table.select())
    migrate_engine.execute(ins)

    table.drop()
    for index in indexes:
        index.create(migrate_engine)

    new_table.rename(table_name)
    deleted = True  # workaround for pyflakes
    new_table.update().\
        where(new_table.c.deleted == deleted).\
        values(deleted=new_table.c.id).\
        execute()

    # NOTE(boris-42): Fix value of deleted column: False -> "" or 0.
    deleted = False  # workaround for pyflakes
    new_table.update().\
        where(new_table.c.deleted == deleted).\
        values(deleted=default_deleted_value).\
        execute()


def get_connect_string(backend, database, user=None, passwd=None,
                       host='localhost'):
    """Get database connection

    Try to get a connection with a very specific set of values, if we get
    these then we'll run the tests, otherwise they are skipped

    DEPRECATED: this function is deprecated and will be removed from oslo_db
    in a few releases. Please use the provisioning system for dealing
    with URLs and database provisioning.

    """
    args = {'backend': backend,
            'user': user,
            'passwd': passwd,
            'host': host,
            'database': database}
    if backend == 'sqlite':
        template = '%(backend)s:///%(database)s'
    else:
        template = "%(backend)s://%(user)s:%(passwd)s@%(host)s/%(database)s"
    return template % args


# def is_backend_avail(backend, database, user=None, passwd=None):
#     """Return True if the given backend is available.
#
#
#     DEPRECATED: this function is deprecated and will be removed from oslo_db
#     in a few releases. Please use the provisioning system to access
#     databases based on backend availability.
#
#     """
#     from oslo_db.sqlalchemy import provision
#
#     connect_uri = get_connect_string(backend=backend,
#                                      database=database,
#                                      user=user,
#                                      passwd=passwd)
#     try:
#         eng = provision.Backend._ensure_backend_available(connect_uri)
#         eng.dispose()
#     except exception.BackendNotAvailable:
#         return False
#     else:
#         return True


def get_db_connection_info(conn_pieces):
    database = conn_pieces.path.strip('/')
    loc_pieces = conn_pieces.netloc.split('@')
    host = loc_pieces[1]

    auth_pieces = loc_pieces[0].split(':')
    user = auth_pieces[0]
    password = ""
    if len(auth_pieces) > 1:
        password = auth_pieces[1].strip()

    return (user, password, database, host)


def index_exists(migrate_engine, table_name, index_name):
    """Check if given index exists.

    :param migrate_engine: sqlalchemy engine
    :param table_name:     name of the table
    :param index_name:     name of the index
    """
    inspector = reflection.Inspector.from_engine(migrate_engine)
    indexes = inspector.get_indexes(table_name)
    index_names = [index['name'] for index in indexes]
    return index_name in index_names


def add_index(migrate_engine, table_name, index_name, idx_columns):
    """Create an index for given columns.

    :param migrate_engine: sqlalchemy engine
    :param table_name:     name of the table
    :param index_name:     name of the index
    :param idx_columns:    tuple with names of columns that will be indexed
    """
    table = get_table(migrate_engine, table_name)
    if not index_exists(migrate_engine, table_name, index_name):
        index = Index(
            index_name, *[getattr(table.c, col) for col in idx_columns]
        )
        index.create()
    else:
        raise ValueError("Index '%s' already exists!" % index_name)


def drop_index(migrate_engine, table_name, index_name):
    """Drop index with given name.

    :param migrate_engine: sqlalchemy engine
    :param table_name:     name of the table
    :param index_name:     name of the index
    """
    table = get_table(migrate_engine, table_name)
    for index in table.indexes:
        if index.name == index_name:
            index.drop()
            break
    else:
        raise ValueError("Index '%s' not found!" % index_name)


def change_index_columns(migrate_engine, table_name, index_name, new_columns):
    """Change set of columns that are indexed by given index.

    :param migrate_engine: sqlalchemy engine
    :param table_name:     name of the table
    :param index_name:     name of the index
    :param new_columns:    tuple with names of columns that will be indexed
    """
    drop_index(migrate_engine, table_name, index_name)
    add_index(migrate_engine, table_name, index_name, new_columns)


def column_exists(engine, table_name, column):
    """Check if table has given column.

    :param engine:         sqlalchemy engine
    :param table_name:     name of the table
    :param column:         name of the colmn
    """
    t = get_table(engine, table_name)
    return column in t.c


class DialectFunctionDispatcher(object):
    @classmethod
    def dispatch_for_dialect(cls, expr, multiple=False):
        """Provide dialect-specific functionality within distinct functions.

        e.g.::

            @dispatch_for_dialect("*")
            def set_special_option(engine):
                pass

            @set_special_option.dispatch_for("sqlite")
            def set_sqlite_special_option(engine):
                return engine.execute("sqlite thing")

            @set_special_option.dispatch_for("mysql+mysqldb")
            def set_mysqldb_special_option(engine):
                return engine.execute("mysqldb thing")

        After the above registration, the ``set_special_option()`` function
        is now a dispatcher, given a SQLAlchemy ``Engine``, ``Connection``,
        URL string, or ``sqlalchemy.engine.URL`` object::

            eng = create_engine('...')
            result = set_special_option(eng)

        The filter system supports two modes, "multiple" and "single".
        The default is "single", and requires that one and only one function
        match for a given backend.    In this mode, the function may also
        have a return value, which will be returned by the top level
        call.

        "multiple" mode, on the other hand, does not support return
        arguments, but allows for any number of matching functions, where
        each function will be called::

            # the initial call sets this up as a "multiple" dispatcher
            @dispatch_for_dialect("*", multiple=True)
            def set_options(engine):
                # set options that apply to *all* engines

            @set_options.dispatch_for("postgresql")
            def set_postgresql_options(engine):
                # set options that apply to all Postgresql engines

            @set_options.dispatch_for("postgresql+psycopg2")
            def set_postgresql_psycopg2_options(engine):
                # set options that apply only to "postgresql+psycopg2"

            @set_options.dispatch_for("*+pyodbc")
            def set_pyodbc_options(engine):
                # set options that apply to all pyodbc backends

        Note that in both modes, any number of additional arguments can be
        accepted by member functions.  For example, to populate a dictionary of
        options, it may be passed in::

            @dispatch_for_dialect("*", multiple=True)
            def set_engine_options(url, opts):
                pass

            @set_engine_options.dispatch_for("mysql+mysqldb")
            def _mysql_set_default_charset_to_utf8(url, opts):
                opts.setdefault('charset', 'utf-8')

            @set_engine_options.dispatch_for("sqlite")
            def _set_sqlite_in_memory_check_same_thread(url, opts):
                if url.database in (None, 'memory'):
                    opts['check_same_thread'] = False

            opts = {}
            set_engine_options(url, opts)

        The driver specifiers are of the form:
        ``<database | *>[+<driver | *>]``.   That is, database name or "*",
        followed by an optional ``+`` sign with driver or "*".   Omitting
        the driver name implies all drivers for that database.

        """
        if multiple:
            cls = DialectMultiFunctionDispatcher
        else:
            cls = DialectSingleFunctionDispatcher
        return cls().dispatch_for(expr)

    _db_plus_driver_reg = re.compile(r'([^+]+?)(?:\+(.+))?$')

    def dispatch_for(self, expr):
        def decorate(fn):
            dbname, driver = self._parse_dispatch(expr)
            if fn is self:
                fn = fn._last
            self._last = fn
            self._register(expr, dbname, driver, fn)
            return self
        return decorate

    def _parse_dispatch(self, text):
        m = self._db_plus_driver_reg.match(text)
        if not m:
            raise ValueError("Couldn't parse database[+driver]: %r" % text)
        return m.group(1) or '*', m.group(2) or '*'

    def __call__(self, *arg, **kw):
        target = arg[0]
        return self._dispatch_on(
            self._url_from_target(target), target, arg, kw)

    def _url_from_target(self, target):
        if isinstance(target, Connectable):
            return target.engine.url
        elif isinstance(target, six.string_types):
            if "://" not in target:
                target_url = sa_url.make_url("%s://" % target)
            else:
                target_url = sa_url.make_url(target)
            return target_url
        elif isinstance(target, sa_url.URL):
            return target
        else:
            raise ValueError("Invalid target type: %r" % target)

    def dispatch_on_drivername(self, drivername):
        """Return a sub-dispatcher for the given drivername.

        This provides a means of calling a different function, such as the
        "*" function, for a given target object that normally refers
        to a sub-function.

        """
        dbname, driver = self._db_plus_driver_reg.match(drivername).group(1, 2)

        def go(*arg, **kw):
            return self._dispatch_on_db_driver(dbname, "*", arg, kw)

        return go

    def _dispatch_on(self, url, target, arg, kw):
        dbname, driver = self._db_plus_driver_reg.match(
            url.drivername).group(1, 2)
        if not driver:
            driver = url.get_dialect().driver

        return self._dispatch_on_db_driver(dbname, driver, arg, kw)

    def _invoke_fn(self, fn, arg, kw):
        return fn(*arg, **kw)


class DialectSingleFunctionDispatcher(DialectFunctionDispatcher):
    def __init__(self):
        self.reg = collections.defaultdict(dict)

    def _register(self, expr, dbname, driver, fn):
        fn_dict = self.reg[dbname]
        if driver in fn_dict:
            raise TypeError("Multiple functions for expression %r" % expr)
        fn_dict[driver] = fn

    def _matches(self, dbname, driver):
        for db in (dbname, '*'):
            subdict = self.reg[db]
            for drv in (driver, '*'):
                if drv in subdict:
                    return subdict[drv]
        else:
            raise ValueError(
                "No default function found for driver: %r" %
                ("%s+%s" % (dbname, driver)))

    def _dispatch_on_db_driver(self, dbname, driver, arg, kw):
        fn = self._matches(dbname, driver)
        return self._invoke_fn(fn, arg, kw)


class DialectMultiFunctionDispatcher(DialectFunctionDispatcher):
    def __init__(self):
        self.reg = collections.defaultdict(
            lambda: collections.defaultdict(list))

    def _register(self, expr, dbname, driver, fn):
        self.reg[dbname][driver].append(fn)

    def _matches(self, dbname, driver):
        if driver != '*':
            drivers = (driver, '*')
        else:
            drivers = ('*', )

        for db in (dbname, '*'):
            subdict = self.reg[db]
            for drv in drivers:
                for fn in subdict[drv]:
                    yield fn

    def _dispatch_on_db_driver(self, dbname, driver, arg, kw):
        for fn in self._matches(dbname, driver):
            if self._invoke_fn(fn, arg, kw) is not None:
                raise TypeError(
                    "Return value not allowed for "
                    "multiple filtered function")


dispatch_for_dialect = DialectFunctionDispatcher.dispatch_for_dialect


def get_non_innodb_tables(connectable, skip_tables=('migrate_version',
                                                    'alembic_version')):
    """Get a list of tables which don't use InnoDB storage engine.

     :param connectable: a SQLAlchemy Engine or a Connection instance
     :param skip_tables: a list of tables which might have a different
                         storage engine
     """

    query_str = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = :database AND
              engine != 'InnoDB'
    """

    params = {}
    if skip_tables:
        params = dict(
            ('skip_%s' % i, table_name)
            for i, table_name in enumerate(skip_tables)
        )

        placeholders = ', '.join(':' + p for p in params)
        query_str += ' AND table_name NOT IN (%s)' % placeholders

    params['database'] = connectable.engine.url.database
    query = text(query_str)
    noninnodb = connectable.execute(query, **params)
    return [i[0] for i in noninnodb]


class NonCommittingConnectable(object):
    """A ``Connectable`` substitute which rolls all operations back.

    ``NonCommittingConnectable`` forms the basis of mock
    ``Engine`` and ``Connection`` objects within a test.   It provides
    only that part of the API that should reasonably be used within
    a single-connection test environment (e.g. no engine.dispose(),
    connection.invalidate(), etc. ).   The connection runs both within
    a transaction as well as a savepoint.   The transaction is there
    so that any operations upon the connection can be rolled back.
    If the test calls begin(), a "pseduo" transaction is returned that
    won't actually commit anything.   The subtransaction is there to allow
    a test to successfully call rollback(), however, where all operations
    to that point will be rolled back and the operations can continue,
    simulating a real rollback while still remaining within a transaction
    external to the test.

    """

    def __init__(self, connection):
        self.connection = connection
        self._trans = connection.begin()
        self._restart_nested()

    def _restart_nested(self):
        self._nested_trans = self.connection.begin_nested()

    def _dispose(self):
        if not self.connection.closed:
            self._nested_trans.rollback()
            self._trans.rollback()
            self.connection.close()

    def execute(self, obj, *multiparams, **params):
        """Executes the given construct and returns a :class:`.ResultProxy`."""

        return self.connection.execute(obj, *multiparams, **params)

    def scalar(self, obj, *multiparams, **params):
        """Executes and returns the first column of the first row."""

        return self.connection.scalar(obj, *multiparams, **params)


class NonCommittingEngine(NonCommittingConnectable):
    """``Engine`` -specific non committing connectbale."""

    @property
    def url(self):
        return self.connection.engine.url

    @property
    def engine(self):
        return self

    def connect(self):
        return NonCommittingConnection(self.connection)

    @contextlib.contextmanager
    def begin(self):
        conn = self.connect()
        trans = conn.begin()
        try:
            yield conn
        except Exception:
            trans.rollback()
        else:
            trans.commit()


class NonCommittingConnection(NonCommittingConnectable):
    """``Connection`` -specific non committing connectbale."""

    def close(self):
        """Close the 'Connection'.

        In this context, close() is a no-op.

        """
        pass

    def begin(self):
        return NonCommittingTransaction(self, self.connection.begin())

    def __enter__(self):
        return self

    def __exit__(self, *arg):
        pass


class NonCommittingTransaction(object):
    """A wrapper for ``Transaction``.

    This is to accommodate being able to guaranteed start a new
    SAVEPOINT when a transaction is rolled back.

    """
    def __init__(self, provisioned, transaction):
        self.provisioned = provisioned
        self.transaction = transaction

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            try:
                self.commit()
            except Exception:
                self.rollback()
                raise
        else:
            self.rollback()

    def commit(self):
        self.transaction.commit()

    def rollback(self):
        self.transaction.rollback()
        self.provisioned._restart_nested()
