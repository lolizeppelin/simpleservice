
TRANSPORT  = None


def init(conf):
    global TRANSPORT, NOTIFICATION_TRANSPORT, NOTIFIER
    exmods = get_allowed_exmods()
    TRANSPORT = oslo_messaging.get_transport(conf,
                                             allowed_remote_exmods=exmods,
                                             aliases=TRANSPORT_ALIASES)
    NOTIFICATION_TRANSPORT = oslo_messaging.get_notification_transport(
        conf, allowed_remote_exmods=exmods, aliases=TRANSPORT_ALIASES)
    serializer = RequestContextSerializer()
    NOTIFIER = oslo_messaging.Notifier(NOTIFICATION_TRANSPORT,
                                       serializer=serializer)

def get_client(target, version_cap=None, serializer=None):
    assert TRANSPORT is not None
    serializer = RequestContextSerializer(serializer)
    return BackingOffClient(TRANSPORT,
                            target,
                            version_cap=version_cap,
                            serializer=serializer)


def get_server(target, endpoints, serializer=None):
    assert TRANSPORT is not None
    serializer = RequestContextSerializer(serializer)
    dispatcher = rpc_dispatcher.RPCDispatcher(target, endpoints, serializer)
    return msg_server.MessageHandlingServer(TRANSPORT, dispatcher, 'eventlet')

get_rpc_server = get_server


def get_notifier(service=None, host=None, publisher_id=None):
    assert NOTIFIER is not None
    if not publisher_id:
        publisher_id = "%s.%s" % (service, host or cfg.CONF.host)
    return NOTIFIER.prepare(publisher_id=publisher_id)