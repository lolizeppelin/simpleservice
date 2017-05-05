import six
import abc

@six.add_metaclass(abc.ABCMeta)
class ManagerBase(object):

    @abc.abstractmethod
    def init_host(self):
        pass

    @abc.abstractmethod
    def after_start(self):
        pass

    @abc.abstractmethod
    def after_stop(self):
        pass

    @abc.abstractmethod
    def periodic_tasks(self):
        return []

    @abc.abstractmethod
    def initialize_service_hook(self, launcherpcservice):
        # check endpoint here
        pass

    def call_endpoint(self, endpoint, method, ctxt, args):
        func = getattr(endpoint, method)
        return func(ctxt, args)

    def full(self):
        return False