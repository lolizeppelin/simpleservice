import psutil
from simpleutil.config import cfg

cpucount = psutil.cpu_count(logical=False)

rpc_client_opts = [
    cfg.IntOpt('rpc_send_timeout',
               default=5,
               min=3, max=10,
               help="Give this number of seconds to socket.settimeout as default "
                    "when Rabbit message send"),
    cfg.IntOpt('rpc_send_retry',
               default=1,
               min=0, max=3,
               help="Rabbit message default send retry times"),
]

rpc_service_opts = [
    cfg.IntOpt('rpc_process',
               default=5,
               min=1,
               max=255,
               help='The number of worker processes to serve the '
                    'rpc process'),
    cfg.IntOpt('rpc_eventlet_pool_size',
               default=64,
               help='Size of eventlet thread pool.')
]

rpc_server_opts = [
    cfg.StrOpt('user',
           default='root',
           help='Rpc Server run user'),
    cfg.StrOpt('group',
           default='root',
           help='Rpc Server run group'),
    cfg.IntOpt('rpc_process',
               default=1,
               min=1,
               max=cpucount*2,
               help='The number of worker processes to serve the rpc process')
]
