import sqlalchemy as sa
from sqlalchemy import orm

from simpleutil.utils import timeutils
from simpleutil.utils import uuidutils

from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.dialects.mysql import BOOLEAN
from sqlalchemy.dialects.mysql import LONGBLOB

from simpleservice.ormdb.models import MyISAMTableBase
from simpleservice.ormdb.models import InnoDBTableBase
from simpleservice.plugin.models import PluginTableBase

from simpleservice.plugin.manager import common as manager_common


class ResponeDetail(PluginTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True),
                         sa.ForeignKey('agentrespones.agent_id', ondelete="CASCADE", onupdate='RESTRICT'),
                         default=0,
                         nullable=False, primary_key=True)
    detail_id = sa.Column(INTEGER(unsigned=True), default=0, primary_key=True, nullable=False)
    result = sa.Column(VARCHAR(manager_common.MAX_DETAIL_RESULT), nullable=False, default='{}')
    __table_args__ = (
            MyISAMTableBase.__table_args__
    )


class AgentRespone(PluginTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True), nullable=False, default=0, primary_key=True)
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


class WsgiRequest(PluginTableBase):
    request_id = sa.Column(VARCHAR(36), default=uuidutils.generate_uuid,
                           nullable=False, primary_key=True)
    request_time = sa.Column(INTEGER(unsigned=True),
                             default=int(timeutils.realnow()), nullable=False)
    # request shoul finish before this time
    deadline = sa.Column(INTEGER(unsigned=True),
                         default=int(timeutils.realnow()) + 10, nullable=False)
    # async resopne checker id, means scheduled timer server id
    async_checker = sa.Column(INTEGER(unsigned=True), default=0, nullable=False)
    # if request finish
    status = sa.Column(BOOLEAN, nullable=False, default=0)
    # number of agent not resopne
    result = sa.Column(VARCHAR(manager_common.MAX_REQUEST_RESULT),
                       nullable=False, default='waiting respone')
    # AgentRespone list
    respones = orm.relationship(AgentRespone, backref='wsgirequest', lazy='select',
                                cascade='delete, delete-orphan')
    __table_args__ = (
        sa.Index('request_time_index', 'request_time'),
        InnoDBTableBase.__table_args__
    )


class AgentResponeBackLog(PluginTableBase):
    """request after deadline scheduled timer will upload a AgentRespone log with time out
    if agent respone affter deadline, will get an error primary key error
    at this time, recode into  agentresponebacklogs table
    """
    agent_id = sa.Column(INTEGER(unsigned=True), nullable=False, default=0, primary_key=True)
    request_id = sa.Column(VARCHAR(36),
                           default=None,
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
            InnoDBTableBase.__table_args__
    )


class AgentEndpoint(PluginTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True),
                         sa.ForeignKey('agents.agent_id', ondelete="CASCADE", onupdate='CASCADE'),
                         default=0,
                         nullable=False,
                         primary_key=True)
    endpoint = sa.Column(VARCHAR(manager_common.MAX_ENDPOINT_NAME_SIZE),
                         default=None,
                         nullable=False, primary_key=True)
    __table_args__ = (
            sa.UniqueConstraint('agent_id'),
            MyISAMTableBase.__table_args__
    )


class AllocedPort(PluginTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True),
                         sa.ForeignKey('agents.agent_id', ondelete="CASCADE", onupdate='CASCADE'),
                         default=0,
                         nullable=False,
                         primary_key=True)
    port = sa.Column(SMALLINT(unsigned=True), nullable=False,
                     default=0,
                     primary_key=True)
    endpoint = sa.Column(VARCHAR(manager_common.MAX_ENDPOINT_NAME_SIZE),
                         nullable=False)
    dynamic = sa.Column(BOOLEAN, default=0, nullable=False)
    port_desc = sa.Column(VARCHAR(256))
    __table_args__ = (
            InnoDBTableBase.__table_args__
    )


class Agent(PluginTableBase):
    agent_id = sa.Column(INTEGER(unsigned=True), nullable=False,
                         default=0,
                         primary_key=True, autoincrement=True)
    create_time = sa.Column(INTEGER(unsigned=True),
                            default=int(timeutils.realnow()), nullable=False)
    host = sa.Column(VARCHAR(manager_common.MAX_HOST_NAME_SIZE), nullable=False)
    # 0 not active, 1 active  -1 mark delete
    status = sa.Column(TINYINT, server_default='0', nullable=False)
    # cpu number
    cpu = sa.Column(INTEGER(unsigned=True), server_default='0', nullable=False)
    # memory can be used
    memory = sa.Column(INTEGER(unsigned=True), server_default='0', nullable=False)
    # disk space can be used
    disk = sa.Column(INTEGER(unsigned=True), server_default='0', nullable=False)
    entiy = sa.Column(INTEGER(unsigned=True), server_default='0', nullable=False)
    static_ports = sa.Column(VARCHAR(manager_common.MAX_PORT_RANGE_SIZE),
                             server_default='[]',
                             nullable=False)
    dynamic_ports = sa.Column(VARCHAR(manager_common.MAX_PORT_RANGE_SIZE),
                              server_default='[]',
                              nullable=False)
    ports = orm.relationship(AllocedPort, backref='agent', lazy='joined',
                             cascade='delete,delete-orphan,save-update')
    endpoints = orm.relationship(AgentEndpoint, backref='agent', lazy='select',
                                 cascade='delete,delete-orphan,save-update')
    __table_args__ = (
            sa.UniqueConstraint('host'),
            InnoDBTableBase.__table_args__
    )


class AgentReportLog(PluginTableBase):
    """Table for recode agent status"""
    # build by Gprimarykey
    report_time = sa.Column(BIGINT(unsigned=True), nullable=False, default=0, primary_key=True)
    agent_id = sa.Column(INTEGER(unsigned=True),
                         sa.ForeignKey('agents.agent_id', ondelete="CASCADE", onupdate='CASCADE'),
                         nullable=False)
    # psutil.process_iter()
    # status()
    # num_fds()
    # num_threads()  num_threads()
    running = sa.Column(INTEGER(unsigned=True), nullable=False)
    sleeping = sa.Column(INTEGER(unsigned=True), nullable=False)
    num_fds = sa.Column(INTEGER(unsigned=True), nullable=False)
    num_threads = sa.Column(INTEGER(unsigned=True), nullable=False)
    # cpu info  count
    # psutil.cpu_stats() ctx_switches interrupts soft_interrupts
    context = sa.Column(INTEGER(unsigned=True), nullable=False)
    interrupts = sa.Column(INTEGER(unsigned=True), nullable=False)
    sinterrupts = sa.Column(INTEGER(unsigned=True), nullable=False)
    # psutil.cpu_times() irq softirq user system nice iowait
    irq = sa.Column(INTEGER(unsigned=True), nullable=False)
    sirq = sa.Column(INTEGER(unsigned=True), nullable=False)
    # percent of cpu time
    user = sa.Column(TINYINT(unsigned=True), nullable=False)
    system = sa.Column(TINYINT(unsigned=True), nullable=False)
    nice = sa.Column(TINYINT(unsigned=True), nullable=False)
    iowait = sa.Column(TINYINT(unsigned=True), nullable=False)
    # mem info  MB
    # psutil.virtual_memory() used cached  buffers free
    used = sa.Column(INTEGER(unsigned=True), nullable=False)
    cached = sa.Column(INTEGER(unsigned=True), nullable=False)
    buffers = sa.Column(INTEGER(unsigned=True), nullable=False)
    free = sa.Column(INTEGER(unsigned=True), nullable=False)
    # network  count
    # psutil.net_connections()  count(*)
    syn = sa.Column(INTEGER(unsigned=True), nullable=False)
    enable = sa.Column(INTEGER(unsigned=True), nullable=False)
    closeing = sa.Column(INTEGER(unsigned=True), nullable=False)

    __table_args__ = (
            sa.Index('agent_id_index', 'agent_id'),
            MyISAMTableBase.__table_args__
    )
