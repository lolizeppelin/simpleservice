import sqlalchemy as sa

from sqlalchemy.ext import declarative

from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.dialects.mysql import LONGBLOB

from simpleservice.ormdb.models import TableBase
from simpleservice.ormdb.models import InnoDBTableBase
from simpleservice.ormdb.models import MyISAMTableBase


PluginTableBase = declarative.declarative_base(cls=TableBase)


class GkeyMap(PluginTableBase):
    """Distribute a sid for host"""
    sid = sa.Column(SMALLINT(unsigned=True), nullable=False,
                    default=1,
                    primary_key=True)
    # Max host size is 253
    host = sa.Column(VARCHAR(253), server_default=None,
                     nullable=True)
    __table_args__ = (
            sa.UniqueConstraint('host', name='unique_host'),
            InnoDBTableBase.__table_args__
    )


class MsgTimeoutRecord(PluginTableBase):
    """Rpc call timeout message recode"""
    record_time = sa.Column(BIGINT(unsigned=True),
                            nullable=False,
                            default=0, primary_key=True)
    msg_id = sa.Column(CHAR(32), nullable=False)
    queue_name = sa.Column(CHAR(38), nullable=False)
    raw_message = sa.Column(LONGBLOB, nullable=True, default=None)
    __table_args__ = (
            MyISAMTableBase.__table_args__
    )
