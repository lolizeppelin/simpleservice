from simpleutil.utils.timeutils import realnow as now

from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice.rpc import common

from simpleservice.rpc.target import Target
from simpleservice.rpc.manager.base import ManagerBase


CONF = cfg.CONF

LOG = logging.getLogger(__name__)

class ServerManager(ManagerBase):

    def __init__(self):
        ManagerBase.__init__(self, 'manager')
        self.target = Target(topic=common.AGENT,
                             namespace=self.namespace)

    def init_host(self):
        if self.target.server is None:
            self.target.server = CONF.host

    def initialize_service_hook(self, rpcservice):
        # check endpoint here
        pass

    def call_endpoint(self, endpoint, method, ctxt, args):
        return {}

    def full(self):
        return False

    def rpc_show(self, ctxt, args):
        print 'get rpc show', ctxt, args
        return {'ret': 'rpc show success'}