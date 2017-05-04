
from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice.rpc import common

from simpleservice.rpc.target import Target
from simpleservice.rpc.manager.base import ManagerBase

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

class ServerManager(ManagerBase):

    def __init__(self):
        self.target = Target(topic=common.AGENT, namespace='manager', server=CONF.host)