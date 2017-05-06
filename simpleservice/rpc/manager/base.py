import six
import abc

@six.add_metaclass(abc.ABCMeta)
class ManagerBase(object):

    def __init__(self, namespace):
        self.namespace = namespace

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

    @abc.abstractmethod
    def call_endpoint(self, endpoint, method, ctxt, args):
        # func = getattr(endpoint, method)
        # return func(ctxt, args)
        pass

    @abc.abstractmethod
    def full(self):
        pass
