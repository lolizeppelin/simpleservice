class Target(object):
    def __init__(self, exchange=None, topic=None, namespace=None,
                 version='1.0', server=None, fanout=None):
        self.exchange = exchange
        self.topic = topic
        self.namespace = namespace
        self.version = version
        # rpc listener must have server
        self.server = server
        self.fanout = fanout

    def __call__(self, **kwargs):
        for a in ('exchange', 'topic', 'namespace',
                  'version', 'server', 'fanout'):
            kwargs.setdefault(a, getattr(self, a))
        return Target(**kwargs)

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        attrs = []
        for a in ['exchange', 'topic', 'namespace',
                  'version', 'server', 'fanout']:
            v = getattr(self, a)
            if v:
                attrs.append((a, v))
        values = ', '.join(['%s=%s' % i for i in attrs])
        return '<Target ' + values + '>'

    def __hash__(self):
        return id(self)


def target_match(send_target, listen_target):
    if send_target.exchange != listen_target.exchange:
        return False
    if send_target.topic != listen_target.topic:
        return False
    if send_target.namespace != listen_target.namespace:
        return False
    if send_target.server not in ('*', listen_target.server):
        return False
    return True