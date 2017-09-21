class Target(object):
    def __init__(self, exchange=None, topic=None, namespace=None,
                 version='1.0', server=None, fanout=None):
        self.exchange = exchange
        self.namespace = namespace
        # self.topic = '%s.%s' % (topic, namespace)
        self.topic = topic
        self.version = version
        # rpc topic listener must have server
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

    def to_dict(self):
        kwargs = dict()
        for a in ('exchange', 'topic', 'namespace',
                  'version', 'server', 'fanout'):
            kwargs.setdefault(a, getattr(self, a))
        return kwargs
