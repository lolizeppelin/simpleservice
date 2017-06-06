from simpleutil.config import cfg


rpc_server_opts = [
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
