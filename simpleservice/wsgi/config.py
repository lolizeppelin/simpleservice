import os
from simpleutil.config import cfg

CONF = cfg.CONF


wsgi_server_options = [
        cfg.StrOpt('wsgi_user',
                   default='nginx',
                   help='Wsgi Server run user'),
        cfg.StrOpt('wsgi_group',
                   default='nginx',
                   help='Wsgi Server run group'),
        cfg.IntOpt('wsgi_process',
                   default=1,
                   min=1,
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
        cfg.StrOpt('wsgi_log_format',
                   default='%(client_ip)s "%(request_line)s" status: '
                           '%(status_code)s  len: %(body_length)s time:'
                           ' %(wall_seconds).7f',
                   help='A python format string that is used as the template to '
                        'generate log lines. The following values can be'
                        'formatted into it: client_ip, date_time, request_line, '
                        'status_code, body_length, wall_seconds.'),
        cfg.IntOpt('tcp_keepidle',
                   default=600,
                   help="Sets the value of TCP_KEEPIDLE in seconds for each "
                        "server socket. Not supported on OS X."),
        cfg.IntOpt('wsgi_default_pool_size',
                   default=100,
                   help="Size of the pool of greenthreads used by wsgi"),
        cfg.IntOpt('max_header_line',
                   default=16384,
                   help="Maximum line size of message headers to be accepted. "
                        "max_header_line may need to be increased when using "
                        "large tokens (typically those generated when keystone "
                        "is configured to use PKI tokens with big service "
                        "catalogs)."),
        cfg.BoolOpt('wsgi_keep_alive',
                    default=True,
                    help="If False, closes the client socket connection "
                         "explicitly."),
        cfg.IntOpt('client_socket_timeout', default=900,
                   help="Timeout for client connections' socket operations. "
                        "If an incoming connection is idle for this number of "
                        "seconds it will be closed. A value of '0' means "
                        "wait forever."),
]


def find_paste_abs(conf):
    # isure paste_deploy config
    if not conf.paste_config:
        raise TypeError('Paste config is None')
    if not os.path.isabs(conf.paste_config):
        paste_path = CONF.find_file(conf.paste_config)
    else:
        paste_path = conf.paste_config
    if not paste_path:
        raise TypeError('Paste config is None')
    return paste_path


def list_opts():
    return wsgi_server_options
