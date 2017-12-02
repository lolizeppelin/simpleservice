import socket
from simpleutil.config import cfg
from simpleutil.log import log

CONF = cfg.CONF

log.register_options(CONF)

default_opts = [
    cfg.HostnameOpt('host',
                    default=socket.gethostname(),
                    help="Hostname to be used by the server, agents and "
                         "services running on this machine. All the agents and "
                         "services running on this machine must use the same "
                         "host value.")
]


service_opts = [
    cfg.BoolOpt('log_options',
                default=True,
                help='Enables or disables logging values of all registered '
                     'options when starting a service (at DEBUG level).'),
    cfg.IntOpt('graceful_shutdown_timeout',
               default=60,
               help='Specify a timeout after which a gracefully shutdown '
                    'server will exit. Zero value means endless wait.'),
]


ntp_opts = [
    cfg.IPOpt('ntp_server',
              help='Specify server ip address of ntp request'
              ),
    cfg.PortOpt('ntp_port',
                default=123,
                help='Specify port of ntp request'
                ),
    cfg.IntOpt('ntp_version',
               default=4,
               help='Specify the version of ntp request',
               min=1,
               max=4,
               ),
    cfg.IntOpt('ntp_timeout',
               default=1,
               help='Specify a timeout for ntp request',
               min=1,
               max=5,
               ),
]


server_cli_opts = [
    cfg.StrOpt('state-path',
               default='/var/run/simpleservice',
               help="Where to store simpleservice state files. "
                    "This directory must be writable by the agent. ")
]

CONF.register_cli_opts(server_cli_opts)

def set_default_for_default_log_levels(extra_log_level_defaults):
    log.set_defaults(default_log_levels=log.get_default_log_levels() + extra_log_level_defaults)


def configure(conf=None):
    if conf is None:
        conf = CONF
    conf.register_opts(default_opts)


def list_opts():
    return server_cli_opts + default_opts + service_opts + ntp_opts
