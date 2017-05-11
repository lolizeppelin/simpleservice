from simpleutil.config import cfg
from simpleutil.log import log as logging
from simpleutil.utils import singleton

from simpleservice.rpc import common
from simpleservice.rpc.plugin.manager.base import ManagerBase
from simpleservice.rpc.target import Target

from simpleservice.ormdb.api import MysqlDriver
from simpleservice.ormdb.config import database_opts

from simpleservice.rpc.plugin.manager.config import manager_group

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


CONF.register_group(manager_group)
CONF.register_opts(database_opts, group=manager_group)


@singleton
class ServerManager(ManagerBase):

    def __init__(self):
        ManagerBase.__init__(self, 'manager')
        self.target = Target(topic=common.AGENT,
                             namespace=self.namespace)
        self.dbdriver = MysqlDriver(self.namespace, CONF.manager)
        self.dbdriver.start()
        self.session = self.dbdriver.session
        self.rsession = self.dbdriver.session

    def init_host(self):
        if self.target.server is None:
            self.target.server = CONF.host

    def after_stop(self):
        self.dbdriver.stop()
    #
    # def initialize_service_hook(self, rpcservice):
    #     # check endpoint here
    #     pass

    def call_endpoint(self, endpoint, method, ctxt, args):
        return {}

    def full(self):
        return False

    def rpc_show(self, ctxt, args):
        print 'get rpc show', ctxt, args
        return {'ret': 'rpc show success'}
