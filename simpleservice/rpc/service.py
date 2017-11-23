import eventlet

from simpleutil.utils import importutils
from simpleutil.utils import threadgroup

from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice import loopingcall
from simpleservice.base import ServiceBase
from simpleservice.base import LauncheServiceBase
from simpleservice.plugin.base import ManagerBase
from simpleservice.rpc.driver.impl import RabbitDriver
from simpleservice.rpc.driver.dispatcher import RPCDispatcher


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class MessageHandlingService(ServiceBase):
    """ MessageHandlingService"""
    def __init__(self, rpcdriver, dispatcher):
        self.conf = rpcdriver.conf
        self.rpcdriver = rpcdriver
        self.dispatcher = dispatcher
        self.listener = None
        self._work_pool = None
        self._ioloop = None
        # self._poll_pool = None
        self._started = False
        super(MessageHandlingService, self).__init__()

    # TODO use automaton @ordered(reset_after='stop')
    def start(self, override_pool_size=None):
        self._started = True
        targets = [self.dispatcher.manager.target, ]
        for endpoint in self.dispatcher.manager.endpoints:
            if hasattr(endpoint, 'target'):
                targets.append(endpoint.target)
        self.listener = self.rpcdriver.listen(targets)
        self._work_pool = \
            threadgroup.ThreadGroup(self.conf.rpc_eventlet_pool_size)
        self._ioloop = eventlet.spawn(self._runner)
        LOG.info("%(class)s started" % {'class': self.__class__.__name__})

    # @ordered(after='start')
    def stop(self):
        self.listener.stop()
        self._started = False

    # @excutils.forever_retry_uncaught_exceptions
    def _runner(self):
        while self._started:
            incoming = self.listener.poll()
            if incoming:
                self._submit_work(self.dispatcher(incoming))
        LOG.debug('MessageHandlingService try stop')
        while True:
            incoming = self.listener.poll()
            if incoming:
                self._submit_work(self.dispatcher(incoming))
            else:
                return

    # @ordered(after='stop')
    def wait(self):
        # wait all self.runner thread finish
        self._ioloop.wait()
        LOG.debug('MessageHandlingService io loop stoped')
        self._work_pool.wait()
        LOG.debug('MessageHandlingService work pool stoped')
        self.listener.cleanup()
        self.dispatcher = None
        self.rpcdriver = None
        LOG.debug('MessageHandlingService has been stoped')

    def _submit_work(self, callback):
        if callback:
            th = self._work_pool.add_thread(callback.run)
            th.link(callback.done)
        # fut.add_done_callback(lambda f: callback.done())

    def reset(self):
        pass


class LauncheRpcServiceBase(LauncheServiceBase):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager.
    """

    def __init__(self, manager, **kwargs):
        plugin_threadpool = kwargs.pop('plugin_threadpool', None)
        if isinstance(manager, basestring):
            self.manager = importutils.import_class(manager)(**kwargs)
        else:
            self.manager = manager
        if not isinstance(manager, ManagerBase):
            raise RuntimeError('Manager type error')
        super(LauncheRpcServiceBase, self).__init__(self.manager.__class__.__name__.lower(),
                                                    plugin_threadpool)
        self.messageservice = None

    @property
    def timers(self):
        return self.manager.timers

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

        for task in self.manager.periodic_tasks:
            periodic = loopingcall.FixedIntervalLoopingCall(task)
            periodic.start(interval=task.periodic_interval,
                           initial_delay=task.initial_delay,
                           stop_on_exception=task.stop_on_exception)
            self.timers.add(periodic)

        self.manager.post_start()

    def __getattr__(self, key):
        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)

    def kill(self):
        """Destroy the service object."""
        self.stop()

    def stop(self):
        LOG.info('Launche rpc service base trying stop')
        if self.messageservice is not None:
            LOG.warning('Message service started, try stop it')
            # Try to shut the connection down, but if we get any sort of
            # errors, go ahead and ignore them.. as we're shutting down anyway
            # This function will call by Launcher from outside
            try:
                self.messageservice.stop()
                LOG.debug('Launche messageservice stoped')
                # self.manager.post_stop()
            except Exception:
                pass
        for x in self.timers:
            x.stop()
        self.manager.post_stop()
        # self.messageservice = None
        if self.plugin_threadpool:
            LOG.debug('Launche rpc service call plugin threadpool stop')
            self.plugin_threadpool.stop(graceful=True)
        LOG.info('Launche rpc service base stoped')

    def wait(self):
        try:
            self.messageservice.wait()
        except Exception:
            pass
        for x in self.timers:
            try:
                x.wait()
            except Exception:
                LOG.exception("Exception occurs when waiting forlaunche rpc service timer")
        # del self.timers[:]
        # del self.endpoints[:]

    def reset(self):
        pass
