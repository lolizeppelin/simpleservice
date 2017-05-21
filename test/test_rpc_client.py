import logging as default_logging

import eventlet

from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice import config


from simpleservice.rpc.service import RPCClientBase
from simpleservice.rpc.target import Target


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


config_file =  'C:\\Users\\loliz_000\\Desktop\\etc\\agent.conf'
config_files=[config_file, ]


# config.set_default_for_default_log_levels(['routes=INFO', ])


CONF(project='rpclient', default_config_files=config_files)
config.configure()
# agent_group = cfg.OptGroup(name='agent', title='agent options')
# CONF.register_group(agent_group)
logging.setup(CONF, 'rpclient')
default_logging.captureWarnings(True)


client = RPCClientBase()

target = Target(namespace='manager', topic='agent')

# ret = client.cast(target, {'request_id':'fuck'}, {'method':'show', 'args':{'data':[1,2,3,4,56]}})
ret = client.call(target, {'request_id':'fuck'}, {'method':'show', 'args':{'data':[1,2,3,4,56]}}, timeout=0.5)
print ret
