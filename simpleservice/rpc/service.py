from simpleservice import loopingcall
from simpleservice.base import LauncheServiceBase
from simpleservice.rpc.config import client_opts
from simpleservice.rpc.config import server_opts
from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver.impl import RabbitDriver
from simpleservice.rpc.server import RpcConnection
from simpleservice.plugin.manager.rpc.base import ManagerBase
from simpleutil.config import cfg
from simpleutil.log import log as logging
from simpleutil.utils import importutils


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class LauncheRpcServiceBase(LauncheServiceBase):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager.
    """

    def __init__(self, manager, endpoints=None,
                 *args, **kwargs):
        self.conf = CONF
        self.conf.register_opts(server_opts)
        self.endpoints = []
        if isinstance(manager, basestring):
            self.manager = importutils.import_class(manager)(*args, **kwargs)
        elif isinstance(manager, ManagerBase):
            self.manager = manager
        else:
            raise RuntimeError('Manager type error')
        if endpoints:
            for endpoint_name in endpoints:
                try:
                    self.endpoints.append(importutils.import_class(endpoint_name)(*args, **kwargs))
                except Exception:
                    raise RuntimeError('Init endpoint %(endpoint)s catch error' % {'endpoint': endpoint_name})
        self.saved_args, self.saved_kwargs = args, kwargs
        self.timers = []
        LauncheServiceBase.__init__(self, self.manager.namespace)

    def start(self):
        self.manager.init_host()
        self.conn = RpcConnection(self.manager, self.endpoints)
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

    def __init__(self, timeout=None, retry=None):
        self.conf = CONF
        self.conf.register_opts(client_opts)
        self.rpcdriver = RabbitDriver(CONF)
        self.timeout = timeout or self.conf.rpc_response_timeout
        self.retry = retry

    def notify(self, target, ctxt, msg):
        try:
            self.rpcdriver.send_notification(target, ctxt, msg, retry=self.retry)
        # except driver_base.TransportDriverError as ex:
        except exceptions.RabbitDriverError as ex:
            raise exceptions.ClientSendError(target, ex)

    def cast(self, target, ctxt, msg):
        """Invoke a method and return immediately. See RPCClient.cast()."""
        try:
            self.rpcdriver.send(target, ctxt, msg,
                                retry=self.retry)
        # except driver_base.TransportDriverError as ex:
        except exceptions.RabbitDriverError as ex:
            raise exceptions.ClientSendError(target, ex)

    def broadcast(self, target, ctxt, msg):
        broadtarget = target(**target.to_dict())
        broadtarget.topic = '%s.*' % broadtarget.topic
        self.cast(broadtarget, ctxt, msg)

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
