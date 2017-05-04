import random

from simpleutil.utils import importutils

from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice import loopingcall
from simpleservice.base import LauncheServiceBase
from simpleservice.rpc.server import RpcConnection


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


DEFAULT_LOG_AFTER = 30


class LauncheRpcServiceBase(LauncheServiceBase):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager.
    """

    def __init__(self, binary, topic, manager, endpoints,
                 # report_interval=None,
                 periodic_interval=None, periodic_fuzzy_delay=None,
                 *args, **kwargs):

        self.binary = binary
        self.endpoints = []

        manager_class = importutils.import_class(manager)
        self.manager = manager_class(host=CONF.host, *args, **kwargs)

        for endpoint_name in endpoints:
            self.endpoints.append(importutils.import_class(endpoint_name)(host=CONF.host, *args, **kwargs))

        # self.report_interval = report_interval
        self.periodic_interval = periodic_interval
        self.periodic_fuzzy_delay = periodic_fuzzy_delay
        self.saved_args, self.saved_kwargs = args, kwargs
        self.timers = []
        LauncheServiceBase.__init__(self, self.binary)
        # super(LauncheRpcServiceBase, self).__init__(host, topic, endpoints=self.endpoints)

    def start(self):
        self.manager.init_host()

        self.conn = RpcConnection(self.manager, self.endpoints)
        LOG.debug("Creating Consumer connection for Service %s",
                  self.topic)
        # self.conn.create_consumer(self.topic, self.endpoints)
        if callable(getattr(self.manager, 'initialize_service_hook', None)):
            self.manager.initialize_service_hook(self)
        self.conn.start()

        # if self.report_interval:
        #     pulse = loopingcall.FixedIntervalLoopingCall(self.report_state)
        #     pulse.start(interval=self.report_interval,
        #                 initial_delay=self.report_interval)
        #     self.timers.append(pulse)

        if self.periodic_interval:
            if self.periodic_fuzzy_delay:
                initial_delay = random.randint(0, self.periodic_fuzzy_delay)
            else:
                initial_delay = None

            periodic = loopingcall.FixedIntervalLoopingCall(self.manager.periodic_tasks)
            periodic.start(interval=self.periodic_interval,
                           initial_delay=initial_delay)
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
        except Exception:
            pass
        for x in self.timers:
            try:
                x.stop()
            except Exception:
                LOG.exception("Exception occurs when timer stops")
        self.timers = []
        del self.endpoints[:]

    def wait(self):
        for x in self.timers:
            try:
                x.wait()
            except Exception:
                LOG.exception("Exception occurs when waiting for timer")

    # def periodic_tasks(self, raise_on_error=False):
    #     """Tasks to be run at a periodic interval."""
    #     ctxt = context.get_admin_context()
    #     self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)

    # def report_state(self):
    #     """Update the state of this service."""
    #     pass

    # def reset(self):
    #     config.reset_service()
