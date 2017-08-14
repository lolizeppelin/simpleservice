class Deliverinterface(object):

    def pre_start(self, external_objects):
        """before external_objects start"""

    def post_start(self):
        """after external_objects start"""

    def post_stop(self):
        """after external_objects stop"""

    def initialize_service_hook(self):
        """"""


class ManagerBase(Deliverinterface):

    agent_type = None

    def __init__(self, target):
        self.target = target
        self.namespace = target.namespace

    def periodic_tasks(self):
        return []

    def add_periodic_task(self, task):
        self.periodic_tasks().append(task)

    def call_endpoint(self, endpoint, method, ctxt, args):
        """Check before call endpoint method, cover it"""
        func = getattr(endpoint, method)
        return func(ctxt, args)

    def full(self):
        """If agent is full load"""
        raise NotImplemented


class EndpointBase(Deliverinterface):
    """"""

    def _entiys(self):
        raise NotImplementedError

    @property
    def entiys(self):
        """return count of entiy"""
        return  self._entiys()