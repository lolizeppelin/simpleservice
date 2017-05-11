import six

from sqlalchemy import Column

from sqlalchemy.orm import object_mapper
from sqlalchemy.ext import declarative

from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.dialects.mysql import BOOLEAN



from simpleutil.utils import timeutils


class ModelBase(six.Iterator):
    """Base class for models."""
    __table_initialized__ = False

    def save(self, session):
        with session.begin(subtransactions=True):
            session.add(self)
            session.flush()

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        # Don't use hasattr() because hasattr() catches any exception, not only
        # AttributeError. We want to passthrough SQLAlchemy exceptions
        # (ex: sqlalchemy.orm.exc.DetachedInstanceError).
        try:
            getattr(self, key)
        except AttributeError:
            return False
        else:
            return True

    def get(self, key, default=None):
        return getattr(self, key, default)

    @property
    def _extra_keys(self):
        """Specifies custom fields

        Subclasses can override this property to return a list
        of custom fields that should be included in their dict
        representation.

        For reference check tests/db/sqlalchemy/test_models.py
        """
        return []

    def __iter__(self):
        columns = list(dict(object_mapper(self).columns).keys())
        # NOTE(russellb): Allow models to specify other keys that can be looked
        # up, beyond the actual db columns.  An example would be the 'name'
        # property for an Instance.
        columns.extend(self._extra_keys)

        return ModelIterator(self, iter(columns))

    def update(self, values):
        """Make the model object behave like a dict."""
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def _as_dict(self):
        """Make the model object behave like a dict.

        Includes attributes from joins.
        """
        local = dict((key, value) for key, value in self)
        joined = dict([(k, v) for k, v in six.iteritems(self.__dict__)
                      if not k[0] == '_'])
        local.update(joined)
        return local

    def iteritems(self):
        """Make the model object behave like a dict."""
        return six.iteritems(self._as_dict())

    def items(self):
        """Make the model object behave like a dict."""
        return self._as_dict().items()

    def keys(self):
        """Make the model object behave like a dict."""
        return [key for key, value in self.iteritems()]


class ModelIterator(six.Iterator):

    def __init__(self, model, columns):
        self.model = model
        self.i = columns

    def __iter__(self):
        return self

    # In Python 3, __next__() has replaced next().
    def __next__(self):
        n = six.advance_iterator(self.i)
        return n, getattr(self.model, n)


class TimestampMixin(object):
    created_at = Column(INTEGER(unsigned=True), default=lambda: int(timeutils.realnow()))
    updated_at = Column(INTEGER(unsigned=True), onupdate=lambda: int(timeutils.realnow()))


class SoftDeleteMixin(object):
    deleted_at = Column(INTEGER(unsigned=True))
    deleted = Column(BOOLEAN, default=0)

    def soft_delete(self, session):
        """Mark this object as deleted."""
        self.deleted = self.id
        self.deleted_at = int(timeutils.realnow())
        self.save(session=session)


class TableBase(ModelBase):

    __table_args__ = {'mysql_engine': 'InnoDB'}

    """Base class for Neutron Models."""
    @declarative.declared_attr
    def __tablename__(cls):
        # NOTE(jkoelker) use the pluralized name of the class as the table
        return cls.__name__.lower() + 's'

    def __iter__(self):
        self._i = iter(object_mapper(self).columns)
        return self

    def next(self):
        n = next(self._i).name
        return n, getattr(self, n)

    __next__ = next

    def __repr__(self):
        """sqlalchemy based automatic __repr__ method."""
        items = ['%s=%r' % (col.name, getattr(self, col.name))
                 for col in self.__table__.columns]
        return "<%s.%s[object at %x] {%s}>" % (self.__class__.__module__,
                                               self.__class__.__name__,
                                               id(self), ', '.join(items))


class __MyISAMTableBase(TableBase):
    __table_args__ = {'mysql_engine': 'MyISAM'}


TableBase = declarative.declarative_base(cls=TableBase)

MyISAMTableBase = declarative.declarative_base(cls=__MyISAMTableBase)