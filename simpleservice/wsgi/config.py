from simpleutil.config import cfg

CONF = cfg.CONF

wsgi_options =  [
        cfg.IntOpt('wsgi_process',
                   default=5,
                   min=1,
                   max=255,
                   help='The number of worker processes to serve the '
                        'wsgi application'),
        cfg.IPOpt('bind_ip',
                  version=4,    # just ipv4
                  default='0.0.0.0',  # nosec : Bind to all interfaces by
                  # default for backwards compatibility.
                  help='The IP address of the network interface for the '
                       'wsgi application listen on.'),
        cfg.PortOpt('bind_port',
                    default=7999,
                    help='The port number which the wsgi application listens '
                         'on.'),
        cfg.StrOpt('paste_config',
                   default='simpleservice-paste.ini',
                   help='Name of the paste configuration file that defines '
                        'the available pipelines.'),
]