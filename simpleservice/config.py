import socket
from simpleutil.config import cfg
from simpleutil.log import log

CONF = cfg.CONF

log.register_options(CONF)

DEFALUT_OPTIONS = [
    cfg.StrOpt('user',
               default='nginx',
               help='Serivce run user'),
    cfg.StrOpt('group',
               default='nginx',
               help='Serivce run group'),
    cfg.HostnameOpt('host',
                    default=socket.gethostname(),
                    help="Hostname to be used by the server, agents and "
                         "services running on this machine. All the agents and "
                         "services running on this machine must use the same "
                         "host value."),
    cfg.StrOpt('state_path',
               default='/var/run/simpleservice',
               help="Where to store simpleservice state files. "
                    "This directory must be writable by the agent. "),
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

def set_default_for_default_log_levels(extra_log_level_defaults):
    log.set_defaults(default_log_levels=log.get_default_log_levels() + extra_log_level_defaults)


def configure(conf=None):
    if conf is None:
        conf = CONF
    conf.register_opts(DEFALUT_OPTIONS)
