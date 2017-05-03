from simpleutil.config import cfg

client_opts = [
    cfg.IntOpt('rpc_response_timeout',
               default=60,
               help='Seconds to wait for a response from a call.')

]

server_opts = [
    cfg.IntOpt('rpc_pool_size',
               default=64,
               help='Size of executor thread pool.')
]
