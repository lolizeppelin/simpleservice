class Deliverinterface(object):

    def __init__(self, target):
        self.target = target
        self.namespace = target.namespace

    def pre_start(self, external_objects):
        """before external_objects start"""

    def post_start(self):
        """after external_objects start"""

    def post_stop(self):
        """after external_objects stop"""

    def initialize_service_hook(self):
        """"""


class ManagerBase(Deliverinterface):
    """Manager Base class"""

    agent_type = None

    def __init__(self, target):
        super(ManagerBase, self).__init__(target)
        self._endpoints = set()
        self._periodic_tasks = []

    @property
    def endpoints(self):
        return self._endpoints

    @property
    def periodic_tasks(self):
        return self._periodic_tasks

    def add_periodic_task(self, task):
        self.periodic_tasks.append(task)

    def call_endpoint(self, endpoint, method, ctxt, **kwargs):
        """Check before call endpoint method, cover it"""
        raise NotImplementedError('Can not call endpoint on this manager')

    def full(self):
        """If agent is full load"""
        raise NotImplementedError('Manager is full now')


class EndpointBase(Deliverinterface):
    """Endpoint base class"""

    @property
    def entitys(self):
        """return count of entitys"""
        raise NotImplementedError('Entitys unkonwn')
