import time
import six
from eventlet import semaphore

from sqlalchemy import func
from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.mysql import base
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.orm.query import orm_exc


from simpleutil.utils import excutils
from simpleutil.utils import reflection
from simpleutil.common.exceptions import InvalidArgument

from simpleutil.log import log as logging

from simpleservice.ormdb import orm
from simpleservice.ormdb import engines
from simpleservice.ormdb import exceptions


LOG = logging.getLogger(__name__)


def safe_for_db_retry(f):
    """Indicate api method as safe for re-connection to database.

    Database connection retries will be enabled for the decorated api method.
    Database connection failure can have many causes, which can be temporary.
    In such cases retry may increase the likelihood of connection.

    Usage::

        @safe_for_db_retry
        def api_method(self):
            self.engine.connect()


    :param f: database api method.
    :type f: function.
    """
    f.__dict__['enable_retry_on_disconnect'] = True
    return f


def retry_on_deadlock(f):
    """Retry a DB API call if Deadlock was received.

    wrap_db_entry will be applied to all db.api functions marked with this
    decorator.
    """
    f.__dict__['enable_retry_on_deadlock'] = True
    return f


def retry_on_request(f):
    """Retry a DB API call if RetryRequest exception was received.

    wrap_db_entry will be applied to all db.api functions marked with this
    decorator.
    """
    f.__dict__['enable_retry_on_request'] = True
    return f


class wrap_db_retry(object):
    """Retry db.api methods, if db_error raised

    Retry decorated db.api methods. This decorator catches db_error and retries
    function in a loop until it succeeds, or until maximum retries count
    will be reached.

    Keyword arguments:

    :param retry_interval: seconds between transaction retries
    :type retry_interval: int or float

    :param max_retries: max number of retries before an error is raised
    :type max_retries: int

    :param inc_retry_interval: determine increase retry interval or not
    :type inc_retry_interval: bool

    :param max_retry_interval: max interval value between retries
    :type max_retry_interval: int or float

    :param exception_checker: checks if an exception should trigger a retry
    :type exception_checker: callable
    """

    def __init__(self, retry_interval=0, max_retries=0,
                 inc_retry_interval=False,
                 max_retry_interval=0, retry_on_disconnect=False,
                 retry_on_deadlock=False, retry_on_request=False,
                 exception_checker=lambda exc: False):
        super(wrap_db_retry, self).__init__()

        self.db_error = ()
        # default is that we re-raise anything unexpected
        self.exception_checker = exception_checker
        if retry_on_disconnect:
            self.db_error += (exceptions.DBConnectionError, )
        if retry_on_deadlock:
            self.db_error += (exceptions.DBDeadlock, )
        if retry_on_request:
            self.db_error += (exceptions.RetryRequest, )
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.inc_retry_interval = inc_retry_interval
        self.max_retry_interval = max_retry_interval

    def __call__(self, f):
        @six.wraps(f)
        def wrapper(*args, **kwargs):
            next_interval = self.retry_interval
            remaining = self.max_retries

            while True:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    with excutils.save_and_reraise_exception() as ectxt:
                        if remaining > 0:
                            ectxt.reraise = not self._is_exception_expected(e)
                        else:
                            LOG.exception('DB exceeded retry limit.')
                            # if it's a RetryRequest, we need to unpack it
                            if isinstance(e, exceptions.RetryRequest):
                                ectxt.type_ = type(e.inner_exc)
                                ectxt.value = e.inner_exc
                    LOG.debug("Performing DB retry for function %s",
                              reflection.get_callable_name(f))
                    # NOTE(vsergeyev): We are using patched time module, so
                    #                  this effectively yields the execution
                    #                  context to another green thread.
                    time.sleep(next_interval)
                    if self.inc_retry_interval:
                        next_interval = min(
                            next_interval * 2,
                            self.max_retry_interval
                        )
                    remaining -= 1

        return wrapper

    def _is_exception_expected(self, exc):
        if isinstance(exc, self.db_error):
            # RetryRequest is application-initated exception
            # and not an error condition in case retries are
            # not exceeded
            if not isinstance(exc, exceptions.RetryRequest):
                LOG.debug('DB error: %s', exc)
            return True
        return self.exception_checker(exc)


class MysqlDriver(object):
    def __init__(self, name, conf, **kwargs):
        self._started = False
        self.conf = conf
        self.name = name
        self._writer_engine = None
        self._reader_engine = None
        self._writer_maker = None
        self._reader_maker = None
        # self._session = None
        # self._rsession = None
        self.connection_kwargs = kwargs
        self.lock = semaphore.Semaphore()

    @property
    def started(self):
        return self._started

    def start(self):
        if not self.started:
            with self.lock:
                if self.started:
                    return
                # use mysqlconnector as connect driver
                self._writer_engine = engines.create_engine('mysql+mysqlconnector://' + self.conf.connection,
                                                            logging_name=self.name,
                                                            debug=self.conf.debug,
                                                            thread_checkin=False,
                                                            idle_timeout=self.conf.idle_timeout,
                                                            max_pool_size=self.conf.max_pool_size,
                                                            max_overflow=self.conf.max_overflow,
                                                            pool_timeout=self.conf.pool_timeout,
                                                            mysql_sql_mode=self.conf.mysql_sql_mode,
                                                            max_retries=self.conf.max_retries,
                                                            retry_interval=self.conf.retry_interval,
                                                            **self.connection_kwargs)
                self._writer_maker = orm.get_maker(engine=self._writer_engine)
                if self.conf.slave_connection:
                    self._reader_engine = engines.create_engine('mysql+mysqlconnector://' + self.conf.slave_connection,
                                                                logging_name=self.name,
                                                                thread_checkin=False,
                                                                idle_timeout=self.conf.idle_timeout,
                                                                max_pool_size=self.conf.max_pool_size,
                                                                max_overflow=self.conf.max_overflow,
                                                                pool_timeout=self.conf.pool_timeout,
                                                                mysql_sql_mode=self.conf.mysql_sql_mode,
                                                                max_retries=self.conf.max_retries,
                                                                retry_interval=self.conf.retry_interval,
                                                                **self.connection_kwargs)
                    self._reader_maker = orm.get_maker(engine=self._reader_engine)
                else:
                    self._reader_engine = self._writer_engine
                    self._reader_maker = self._writer_maker
                self._started = True

    def stop(self):
        if self.started:
            with self.lock:
                if not self.started:
                    return
                self._writer_engine = None
                self._reader_engine = None
                self._writer_maker = None
                self._reader_maker = None
                self._started = False

    def _get_sessionmaker(self, read=False):
        """Get the sessionmaker instance used to create a Session.

        This can be called for those cases where the sessionmaker() is to
        be temporarily injected with some state such as a specific connection.

        """
        if read:
            return self._reader_maker
        else:
            return self._writer_maker

    def get_session(self, read=False, **kwargs):
        if not self.started:
            self.start()
        return self._get_sessionmaker(read)(**kwargs)


def filter_query(query, model, filter=None):
    if filter is not None:
        if isinstance(filter, (BooleanClauseList, BinaryExpression)):
            query = query.filter(filter)
        elif isinstance(filter, (list, tuple, set)):
            query = query.filter(*filter)
        elif isinstance(filter, dict):
            if isinstance(model, (list, tuple, set)):
                model = model[0].class_
            try:
                query = query.filter(*[model.__dict__[key] == filter[key] for key in filter])
            except KeyError as e:
                raise exceptions.ColumnError('No such attribute ~%(attribute)s~ in %(class)s class' %
                                             {'attribute': e.message, 'class': model.__name__})
        elif callable(filter):
            try:
                query = query.filter(filter(model))
            except Exception:
                raise InvalidArgument('call filter function catch error')
        else:
            raise InvalidArgument('filter type %s not match' % type(filter).__name__)
    return query


def model_query(session, model, filter=None, timeout=1.0):
    """filter_args is can be a dict of model's attribte
    or a callable function form return the args for query.filter
    """
    if not isinstance(session, Session):
        raise InvalidArgument('First must Session of sqlalchemy')
    if isinstance(model, (list, tuple, set)):
        query = session.query(*model)
    else:
        query = session.query(model)
    # TODO timeout for mysql query
    # if timeout:
    #     query = query.execution_options(timeout=timeout)
    return filter_query(query, model, filter)


def model_max_with_key(session, modelkey, filter=None, timeout=0.1):
    """model can be DeclarativeMeta of table
    or InstrumentedAttribute of table column
    """
    if not isinstance(modelkey, InstrumentedAttribute):
        raise InvalidArgument('modelkey type error')
    if not isinstance(modelkey.property, ColumnProperty):
        raise InvalidArgument('modelkey type error')
    column = modelkey.property.columns[0]
    column_type = column.type
    if not isinstance(column_type, base._IntegerType):
        raise InvalidArgument('%s column type error, not allow autoincrement' % str(column))
    return model_query(session, func.max(modelkey), filter, timeout).scalar() or 0


def model_autoincrement_id(session, modelkey, filter=None, timeout=0.1):
    try:
        return model_max_with_key(session, modelkey, filter, timeout) + 1
    except orm_exc.NoResultFound:
        column = modelkey.property.columns[0]
        if column.default is not None:
            if column.default.is_callable:
                try:
                    default_id = column.default.arg()
                except TypeError:
                    raise InvalidArgument('%s call default function' % str(column))
            else:
                default_id = column.default.arg
        else:
            if column.type.unsigned:
                default_id = 0
            else:
                # TODO find min value of column
                default_id = 0
        return default_id


def model_count_with_key(session, model, filter=None, timeout=0.1):
    """model can be DeclarativeMeta of table
    or InstrumentedAttribute of table column
    """
    if isinstance(model, DeclarativeMeta):
        query = filter_query(session.query(func.count("*")).select_from(model), model, filter)
    elif isinstance(model, InstrumentedAttribute):
        query = model_query(session, func.count(model), filter, timeout)
        # model = model.class_
    else:
        raise InvalidArgument('model type error')
    # query = session.query(func.count(key)).select_from(model)
    return query.scalar() or 0
