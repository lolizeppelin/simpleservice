class ManagerBase(object):

    def __init__(self, target):
        self.target = target
        self.namespace = target.namespace

    def init_host(self):
        pass

    def after_start(self):
        pass

    def after_stop(self):
        pass

    def periodic_tasks(self):
        return []

    def initialize_service_hook(self, rpcservice):
        # check endpoint here
        pass

    def call_endpoint(self, endpoint, method, ctxt, args):
        """Check before call endpoint method, cover it"""
        func = getattr(endpoint, method)
        return func(ctxt, args)

    def full(self):
        """If agent is full load"""
        raise NotImplemented
