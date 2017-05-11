import logging as default_logging

from simpleservice import config
from simpleservice.rpc.plugin.manager import server
from simpleservice.rpc.service import LauncheRpcServiceBase
from simpleservice.server import ServerWrapper
from simpleservice.server import launch
from simpleutil.config import cfg
from simpleutil.log import log as logging


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


config_file =  'C:\\Users\\loliz_000\\Desktop\\etc\\agent.conf'
config_files=[config_file, ]


# config.set_default_for_default_log_levels(['routes=INFO', ])


CONF(project='agent', default_config_files=config_files)
config.configure()
agent_group = cfg.OptGroup(name='agent', title='agent options')
CONF.register_group(agent_group)
logging.setup(CONF, 'agent')
default_logging.captureWarnings(True)


servers = []
manager = server.ServerManager()
rpc_server = LauncheRpcServiceBase(manager)
wsgi_wrapper = ServerWrapper(rpc_server, workers=1)
servers.append(wsgi_wrapper)
launch(servers)


