from simpleutil.utils import importutils
from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice import loopingcall
from simpleservice.base import LauncheServiceBase
from simpleservice.plugin.base import ManagerBase
from simpleservice.plugin.base import EndpointBase
from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver.impl import RabbitDriver
from simpleservice.rpc.driver.dispatcher import RPCDispatcher
from simpleservice.rpc.server import MessageHandlingService


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class LauncheRpcServiceBase(LauncheServiceBase):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager.
    """

    def __init__(self, manager, endpoints=None,
                 *args, **kwargs):
        self.endpoints = set()
        if isinstance(manager, basestring):
            self.manager = importutils.import_class(manager)(*args, **kwargs)
        else:
            self.manager = manager
        if not isinstance(manager, ManagerBase):
            raise RuntimeError('Manager type error')
        if endpoints:
            endpoints = set(list(endpoints))
            while endpoints:
                endpoint_name = endpoints.pop(0)
                if isinstance(endpoint_name, basestring):
                    endpoint = importutils.import_class(endpoint_name)(*args, **kwargs)
                else:
                    endpoint = endpoint_name
                if not isinstance(endpoint, EndpointBase):
                    RuntimeError('Endpoint type error')
                self.endpoints.add(endpoint())
        self.saved_args, self.saved_kwargs = args, kwargs
        self.timers = []
        super(LauncheRpcServiceBase, self).__init__(self.manager.namespace)
        self.messageservice = None


    def start(self):
        self.manager.pre_start(self)
        # if process not a forked process
        if hasattr(self.manager, 'rabbit_conf'):
            rabbit_conf = self.manager.rabbit_conf
        else:
            rabbit_conf = CONF.rabbit
        self.messageservice = MessageHandlingService(rpcdriver=RabbitDriver(rabbit_conf),
                                                     dispatcher=RPCDispatcher(self.manager))
        LOG.debug("Creating Consumer connection for Service %s",
                  self.manager.target.topic)

        self.manager.initialize_service_hook()

        self.messageservice.start()

        for task in self.manager.periodic_tasks():
            periodic = loopingcall.FixedIntervalLoopingCall(task)
            periodic.start(interval=task.periodic_interval,
                           initial_delay=task.initial_delay,
                           stop_on_exception=task.stop_on_exception)
            self.timers.append(periodic)

        self.manager.post_start()

    def __getattr__(self, key):
        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)

    def kill(self):
        """Destroy the service object."""
        self.stop()

    def stop(self):
        if self.messageservice is None:
            raise RuntimeError('Service not started? conn is None')
        # Try to shut the connection down, but if we get any sort of
        # errors, go ahead and ignore them.. as we're shutting down anyway
        # This function will call by Launcher from outside
        try:
            self.messageservice.stop()
            self.messageservice.wait()
            # self.manager.post_stop()
        except Exception:
            pass
        for x in self.timers:
            try:
                x.stop()
            except Exception:
                LOG.exception("Exception occurs when timer stops")
        self.manager.post_stop()
        self.messageservice = None

    def wait(self):
        for x in self.timers:
            try:
                x.wait()
            except Exception:
                LOG.exception("Exception occurs when waiting for timer")
        # del self.timers[:]
        # del self.endpoints[:]

    def reset(self):
        pass


class RPCClientBase(object):

    def __init__(self, conf, timeout=None, retry=None):
        self.conf = conf
        self.rpcdriver = RabbitDriver(conf)
        self.timeout = timeout or conf.rpc_call_timeout
        self.retry = retry or conf.rpc_send_retry

    def notify(self, target, ctxt, msg):
        try:
            self.rpcdriver.send_notification(target, ctxt, msg, retry=self.retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.ClientSendError(target, ex)

    def cast(self, target, ctxt, msg):
        """Invoke a method and return immediately. See RPCClient.cast()."""
        try:
            self.rpcdriver.send(target, ctxt, msg,
                                retry=self.retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.ClientSendError(target, ex)

    def call(self, target, ctxt, msg, timeout=None):
        if target.fanout:
            raise exceptions.InvalidTarget('A call cannot be used with fanout', target)
        timeout = timeout or self.timeout
        try:
            return self.rpcdriver.send(target, ctxt, msg,
                                       wait_for_reply=True, timeout=timeout,
                                       retry=self.retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.ClientSendError(target, ex)
