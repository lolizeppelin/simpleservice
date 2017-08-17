from simpleutil.config import cfg

CONF = cfg.CONF


rabbit_opts = [

    cfg.StrOpt('rabbit_host',
               default='localhost',
               help='The RabbitMQ broker address where a single node is '
                    'used.'),
    cfg.PortOpt('rabbit_port',
                default=5672,
                help='The RabbitMQ broker port where a single node is used.'),
    cfg.StrOpt('rabbit_userid',
               default='guest',
               help='The RabbitMQ userid.'),
    cfg.StrOpt('rabbit_password',
               default='guest',
               help='The RabbitMQ password.',
               secret=True),
    cfg.StrOpt('rabbit_virtual_host',
               default='simpleservice',
               help='The RabbitMQ virtual host.'),
    cfg.StrOpt('exchange',
               default='simpleservice',
               help='The default exchange under which topics are scoped. May '
                    'be overridden by an exchange name specified in the '
                    'transport_url option.'),

    cfg.StrOpt('rabbit_login_method',
               default='AMQPLAIN',
               help='The RabbitMQ login method.'),
    cfg.BoolOpt('rabbit_ha_queues',
                default=False,
                help='Try to use HA queues in RabbitMQ (x-ha-policy: all). '
                'If you change this option, you must wipe the RabbitMQ '
                'database. In RabbitMQ 3.0, queue mirroring is no longer '
                'controlled by the x-ha-policy argument when declaring a '
                'queue. If you just want to make sure that all queues (except '
                ' those with auto-generated names) are mirrored across all '
                'nodes, run: '
                """\"rabbitmqctl set_policy HA '^(?!amq\.).*' """
                """'{"ha-mode": "all"}' \""""),


    cfg.FloatOpt('kombu_reconnect_delay',
                 default=0.5,
                 help='How long to wait before reconnecting in response to an '
                      'AMQP consumer cancel notification.'),
    cfg.IntOpt('kombu_missing_consumer_retry_timeout',
               default=5,
               help='How long to wait a missing client beforce abandoning to '
                    'send it its replies. This value should not be longer '
                    'than rpc_send_timeout.'),
    cfg.StrOpt('kombu_failover_strategy',
               choices=('round-robin', 'shuffle'),
               default='round-robin',
               help='Determines how the next RabbitMQ node is chosen in case '
                    'the one we are currently connected to becomes '
                    'unavailable. Takes effect only if more than one '
                    'RabbitMQ node is provided in config.'),
    cfg.IntOpt('rabbit_retry_interval',
               default=1,
               help='How frequently to retry connecting with RabbitMQ.'),
    cfg.IntOpt('rabbit_retry_backoff',
               default=1,
               help='How long to backoff for between retries when connecting '
                    'to RabbitMQ.'),
    cfg.IntOpt('rabbit_interval_max',
               default=2,
               help='Maximum interval of RabbitMQ connection retries. '
                    'Default is 3 seconds.'),
    cfg.IntOpt('rabbit_max_retries',
               default=5,
               help='Maximum number of RabbitMQ connection retries. '
                    'Default is 0 (infinite retry count).'),
    cfg.IntOpt('rabbit_transient_queues_ttl',
               min=1,
               default=300,
               help='Positive integer representing duration in seconds for '
                    'queue TTL (x-expires). Queues which are unused for the '
                    'duration of the TTL are automatically deleted. The '
                    'parameter affects only reply and fanout queues.'),
    cfg.FloatOpt('rabbit_connect_timeout',
                 default=0.5,
                 help='Timeout connect to rabbit server'),
    cfg.IntOpt('rabbit_qos_prefetch_count',
               default=0,
               help='Specifies the number of messages to prefetch. Setting to '
                    'zero allows unlimited messages.'),
    cfg.IntOpt('heartbeat_timeout_threshold',
               default=30,
               help="Number of seconds after which the Rabbit broker is "
               "considered down if heartbeat's keep-alive fails "
               "(0 disable the heartbeat). EXPERIMENTAL"),
    cfg.IntOpt('heartbeat_rate',
               default=2,
               help='How often times during the heartbeat_timeout_threshold '
               'we check the heartbeat.'),


    cfg.StrOpt('kombu_compression',
               help="EXPERIMENTAL: Possible values are: gzip, bz2. If not "
                    "set compression will not be used. This option may not"
                    "be available in future versions."),


    cfg.BoolOpt('rabbit_use_ssl',
                default=False,
                help='Connect over SSL for RabbitMQ.'),
    cfg.StrOpt('kombu_ssl_version',
               default='',
               help='SSL version to use (valid only if SSL enabled). '
                    'Valid values are TLSv1 and SSLv23. SSLv2, SSLv3, '
                    'TLSv1_1, and TLSv1_2 may be available on some '
                    'distributions.'
               ),
    cfg.StrOpt('kombu_ssl_keyfile',
               default='',
               help='SSL key file (valid only if SSL enabled).'),
    cfg.StrOpt('kombu_ssl_certfile',
               default='',
               help='SSL cert file (valid only if SSL enabled).'),
    cfg.StrOpt('kombu_ssl_ca_certs',
               default='',
               help='SSL certification authority file '
                    '(valid only if SSL enabled).'),
]

amqp_opts = [
    cfg.BoolOpt('amqp_durable_queues',
                default=False,
                help='Use durable queues in AMQP.'),
    cfg.BoolOpt('amqp_auto_delete',
                default=False,
                help='Auto-delete queues in AMQP.'),
]

rpc_base_opts = [
    cfg.IntOpt('rabbit_conn_pool_size',
               default=30,
               help='Size of rabbit RPC connection pool for send rpc request.'),
]
