import sqlalchemy as sa

from sqlalchemy.ext import declarative

from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.dialects.mysql import INTEGER

from simpleservice.ormdb.models import TableBase
from simpleservice.ormdb.models import InnoDBTableBase

from simpleservice.plugin.manager import common as manager_common


PluginTableBase = declarative.declarative_base(cls=TableBase)


class GkeyMap(PluginTableBase):
    """Distribute a sid for host"""
    sid = sa.Column(INTEGER(unsigned=True), nullable=False,
                    default=0,
                    primary_key=True)
    host = sa.Column(VARCHAR(manager_common.MAX_HOST_NAME_SIZE), server_default=None,
                     nullable=True)
    __table_args__ = (
            sa.UniqueConstraint('host'),
            InnoDBTableBase.__table_args__
    )