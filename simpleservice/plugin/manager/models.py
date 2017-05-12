import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext import declarative

from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import BOOLEAN
from sqlalchemy.dialects.mysql import LONGBLOB

from simpleutil.utils import timeutils

from simpleservice.ormdb.models import TableBase
from simpleservice.ormdb.models import MyISAMTableBase

from simpleservice.plugin.manager import common as manager_common


ManagerTableBase = declarative.declarative_base(cls=TableBase)


class ResponeDetail(ManagerTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True),
                         sa.ForeignKey('agentrespones.agent_id', ondelete="CASCADE", onupdate='RESTRICT'),
                         nullable=False, primary_key=True)
    detail_id = sa.Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    result = sa.Column(VARCHAR(manager_common.MAX_DETAIL_RESULT), nullable=False, default='{}')
    __table_args__ = (
            MyISAMTableBase.__table_args__
    )


class AgentRespone(ManagerTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True), nullable=False, primary_key=True)
    request_id = sa.Column(VARCHAR(36),
                           sa.ForeignKey('wsgirequests.request_id', ondelete="RESTRICT", onupdate='RESTRICT'),
                           nullable=False, primary_key=True)
    server_time = sa.Column(INTEGER(unsigned=True), default=int(timeutils.realnow()), nullable=False)
    agent_time = sa.Column(INTEGER(unsigned=True), nullable=False)
    result = sa.Column(VARCHAR(manager_common.MAX_AGENT_RESULT),
                       nullable=False, default='agent respone rpc request')
    # agent respone
    # if status is 0, means this build by async resopne checker
    # not by real agent
    status = sa.Column(BOOLEAN, nullable=False, default=0)
    details = orm.relationship(ResponeDetail, backref='agentrespone', lazy='select',
                               cascade='delete')
    __table_args__ = (
            sa.Index('request_id_index', 'request_id'),
            MyISAMTableBase.__table_args__
    )


class WsgiRequest(ManagerTableBase):
    request_id = sa.Column(VARCHAR(36),
                           nullable=False, primary_key=True)
    request_time = sa.Column(INTEGER(unsigned=True),
                             default=int(timeutils.realnow()), nullable=False)
    # request shoul finish before this time
    deadline = sa.Column(INTEGER(unsigned=True),
                         default=int(timeutils.realnow()), nullable=False)
    # async resopne checker id, means scheduled timer server id
    async_checker = sa.Column(INTEGER(unsigned=True), default=0, nullable=False)
    # if request finish
    status = sa.Column(BOOLEAN, nullable=False, default=0)
    # number of agent not resopne
    unrespone = sa.Column(INTEGER(unsigned=True), default=0, nullable=False)
    result = sa.Column(VARCHAR(manager_common.MAX_REQUEST_RESULT),
                       nullable=False, default='waiting respone')
    # AgentRespone list
    respones = orm.relationship(AgentRespone, backref='wsgirequest', lazy='select',
                                cascade='delete, delete-orphan')


class AgentResponeBackLog(ManagerTableBase):
    """request after deadline scheduled timer will upload a AgentRespone log with time out
    if agent respone affter deadline, will get an error primary key error
    at this time, recode into  agentresponebacklogs table
    """
    agent_id = sa.Column(INTEGER(unsigned=True), nullable=False, primary_key=True)
    request_id = sa.Column(VARCHAR(36),
                           nullable=False, primary_key=True)
    server_time = sa.Column(INTEGER(unsigned=True), default=int(timeutils.realnow()), nullable=False)
    agent_time = sa.Column(INTEGER(unsigned=True), nullable=False)
    result = sa.Column(VARCHAR(manager_common.MAX_AGENT_RESULT),
                       nullable=False, default='agent respone rpc request')
    status = sa.Column(BOOLEAN, nullable=False, default=0)
    # will not link to ResponeDetail
    # save respone detail into LONGBLOB column
    details = sa.Column(LONGBLOB, nullable=True)
    __table_args__ = (
            sa.Index('request_id_index', 'request_id'),
            TableBase.__table_args__
    )


class AgentEndpoint(ManagerTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True),
                         sa.ForeignKey('agents.agent_id', ondelete="CASCADE", onupdate='CASCADE'),
                         nullable=True,
                         primary_key=True)
    endpoint = sa.Column(VARCHAR(manager_common.MAX_ENDPOINT_NAME_SIZE),
                         nullable=False, primary_key=True)
    __table_args__ = (
            sa.UniqueConstraint('agent_id'),
            TableBase.__table_args__
    )


class AllocedPort(ManagerTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True),
                         sa.ForeignKey('agents.agent_id', ondelete="CASCADE", onupdate='CASCADE'),
                         nullable=True,
                         primary_key=True)
    port = sa.Column(SMALLINT(unsigned=True), nullable=False, primary_key=True)
    dynamic = sa.Column(BOOLEAN, nullable=False)


class Agent(ManagerTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True), nullable=True,
                         primary_key=True, autoincrement=True)
    host = sa.Column(VARCHAR(256), nullable=False)
    # 0 not active, 1 active
    status = sa.Column(BOOLEAN, nullable=False, default=1)
    disk = sa.Column(VARCHAR(256), nullable=False)
    entiy = sa.Column(VARCHAR(256), nullable=False)
    load = sa.Column(VARCHAR(256), nullable=False)
    memory = sa.Column(VARCHAR(256), nullable=False)
    static_ports = sa.Column(VARCHAR(1024), nullable=True)
    dynamic_ports = sa.Column(VARCHAR(1024), nullable=True)
    ports = orm.relationship(AllocedPort, backref='agent', lazy='joined',
                             cascade='delete,delete-orphan,save-update')
    endpoints = orm.relationship(AgentEndpoint, backref='agent', lazy='select',
                                 cascade='delete,delete-orphan,save-update')
    __table_args__ = (
            sa.UniqueConstraint('agent_id'),
            TableBase.__table_args__
    )
