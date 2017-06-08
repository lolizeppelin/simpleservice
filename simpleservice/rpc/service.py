from simpleservice import loopingcall
from simpleservice.base import LauncheServiceBase
from simpleservice.plugin.base import ManagerBase
from simpleservice.plugin.base import EndpointBase
from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver.impl import RabbitDriver
from simpleservice.rpc.server import RpcConnection
from simpleutil.log import log as logging
from simpleutil.utils import importutils


LOG = logging.getLogger(__name__)


class LauncheRpcServiceBase(LauncheServiceBase):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager.
    """

    def __init__(self, conf, manager, endpoints=None,
                 *args, **kwargs):
        self.conf = conf
        self.endpoints = []
        if isinstance(manager, basestring):
            self.manager = importutils.import_class(manager)(*args, **kwargs)
        else:
            self.manager = manager
        if not isinstance(manager, ManagerBase):
            raise RuntimeError('Manager type error')
        if endpoints:
            for endpoint_name in endpoints:
                if isinstance(endpoint_name, basestring):
                    endpoint = importutils.import_class(endpoint_name)(*args, **kwargs)
                else:
                    endpoint = endpoint_name
                if not isinstance(endpoint, EndpointBase):
                    RuntimeError('Endpoint type error')
                self.endpoints.append(endpoint)
        self.saved_args, self.saved_kwargs = args, kwargs
        self.timers = []
        LauncheServiceBase.__init__(self, self.manager.namespace)

    def start(self):
        self.manager.init_host()
        self.conn = RpcConnection(self.conf, self.manager, self.endpoints)
        LOG.debug("Creating Consumer connection for Service %s",
                  self.manager.target.topic)
        self.manager.initialize_service_hook(self)
        self.conn.start()

        # task must callable
        for task in self.manager.periodic_tasks():
            periodic = loopingcall.FixedIntervalLoopingCall(task)
            periodic.start(interval=task.periodic_interval,
                           initial_delay=task.initial_delay)
            self.timers.append(periodic)

        self.manager.after_start()

    def __getattr__(self, key):
        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)

    def kill(self):
        """Destroy the service object."""
        self.stop()

    def stop(self):
        # Try to shut the connection down, but if we get any sort of
        # errors, go ahead and ignore them.. as we're shutting down anyway
        # This function will call by Launcher from outside
        try:
            self.conn.close()
            self.manager.after_stop()
        except Exception:
            pass
        for x in self.timers:
            try:
                x.stop()
            except Exception:
                LOG.exception("Exception occurs when timer stops")
        del self.timers[:]
        del self.endpoints[:]

    def wait(self):
        for x in self.timers:
            try:
                x.wait()
            except Exception:
                LOG.exception("Exception occurs when waiting for timer")

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
