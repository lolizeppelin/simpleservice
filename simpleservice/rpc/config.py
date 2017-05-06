import socket
from simpleutil.config import cfg

client_opts = [
    cfg.IntOpt('rpc_response_timeout',
               default=60,
               help='Seconds to wait for a response from a call.')

]

server_opts = [
    cfg.HostnameOpt('host',
                    default=socket.gethostname(),
                    help="Hostname to be used by the Center server, agents and "
                         "services running on this machine. All the agents and "
                         "services running on this machine must use the same "
                         "host value."),

    cfg.IntOpt('rpc_eventlet_pool_size',
               default=64,
               help='Size of eventlet thread pool.')
]
