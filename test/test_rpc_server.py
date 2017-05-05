

from simpleservice.rpc.service import LauncheRpcServiceBase

from simpleservice.rpc.manager import server

from simpleservice.server import launch
from simpleservice.server import ServerWrapper


import os

import logging
from simpleutil.config import cfg
from simpleutil.log import log

from simpleservice import config
from simpleservice.server import ServerWrapper
from simpleservice.server import launch
from simpleservice.rpc.config import server_opts

CONF = cfg.CONF
LOG = log.getLogger(__name__)


config_file =  'C:\\Users\\loliz_000\\Desktop\\etc\\agent.conf'
config_files=[config_file, ]


config.set_default_for_default_log_levels(['routes=INFO', ])



CONF(project='center', default_config_files=config_files)
config.configure()
agent_group = cfg.OptGroup(name='agent', title='agent options')
CONF.register_group(agent_group)
log.setup(CONF, 'agent')
CONF.register_opts(server_opts)
logging.captureWarnings(True)


servers = []
manager = server.ServerManager()
rpc_server = LauncheRpcServiceBase(manager)
wsgi_wrapper = ServerWrapper(rpc_server, 1)
servers.append(wsgi_wrapper)
launch(servers)


