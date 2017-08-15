import functools
import inspect
import traceback

import eventlet
from eventlet.semaphore import Semaphore


from simpleutil.utils import importutils
from simpleutil.utils import lockutils
from simpleutil.utils import threadgroup
from simpleutil.utils import timeutils

from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice import loopingcall
from simpleservice.base import ServiceBase
from simpleservice.base import LauncheServiceBase
from simpleservice.plugin.base import ManagerBase
from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver.impl import RabbitDriver
from simpleservice.rpc.driver.dispatcher import RPCDispatcher


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


DEFAULT_LOG_AFTER = 30


class _OrderedTask(object):
    """A task which must be executed in a particular order.

    A caller may wait for this task to complete by calling
    `wait_for_completion`.

    A caller may run this task with `run_once`, which will ensure that however
    many times the task is called it only runs once. Simultaneous callers will
    block until the running task completes, which means that any caller can be
    sure that the task has completed after run_once returns.
    """

    INIT = 0      # The task has not yet started
    RUNNING = 1   # The task is running somewhere
    COMPLETE = 2  # The task has run somewhere

    def __init__(self, name):
        """Create a new _OrderedTask.
        :param name: The name of this task. Used in log messages.
        """
        super(_OrderedTask, self).__init__()

        self._name = name
        # self._cond = threading.Condition()
        self._cond = lockutils.OrderedLock()
        self._state = self.INIT

    def _wait(self, condition, msg, log_after, timeout_timer):

        log_timer = None
        if log_after != 0:
            log_timer = timeutils.StopWatch(duration=log_after)
            log_timer.start()

        while condition():
            if log_timer is not None and log_timer.expired():
                LOG.warning('Possible hang: %s', msg)
                LOG.debug(''.join(traceback.format_stack()))
                # Only log once. After than we wait indefinitely without
                # logging.
                log_timer = None

            if timeout_timer is not None and timeout_timer.expired():
                raise exceptions.TaskTimeout(msg)

            timeouts = []
            if log_timer is not None:
                timeouts.append(log_timer.leftover())
            if timeout_timer is not None:
                timeouts.append(timeout_timer.leftover())

            wait = None
            if timeouts:
                wait = min(timeouts)
            self._cond.wait(wait)

    @property
    def complete(self):
        return self._state == self.COMPLETE

    def wait_for_completion(self, caller, log_after, timeout_timer):
        with self._cond:
            msg = '%s is waiting for %s to complete' % (caller, self._name)
            self._wait(lambda: not self.complete,
                       msg, log_after, timeout_timer)

    def run_once(self, fn, log_after, timeout_timer):
        with self._cond:
            if self._state == self.INIT:
                self._state = self.RUNNING
                self._cond.release()
                try:
                    post_fn = fn()
                finally:
                    self._cond.acquire()
                    self._state = self.COMPLETE
                    self._cond.notify_all()

                if post_fn is not None:
                    # Release the condition lock before calling out to prevent
                    # deadlocks. Reacquire it immediately afterwards.
                    self._cond.release()
                    try:
                        post_fn()
                    finally:
                        self._cond.acquire()
            elif self._state == self.RUNNING:
                msg = ('%s is waiting for another thread to complete'
                       % self._name)
                self._wait(lambda: self._state == self.RUNNING,
                           msg, log_after, timeout_timer)


class _OrderedTaskRunner(object):
    def __init__(self, *args, **kwargs):
        # super(_OrderedTaskRunner, self).__init__(*args, **kwargs)
        self._tasks = [name
                       for (name, member) in inspect.getmembers(self)
                       if inspect.ismethod(member) and
                       getattr(member, '_ordered', False)]
        self._states = {}
        self.reset_states()
        # self._reset_lock = threading.Lock()
        self._reset_lock = Semaphore()

    def reset_states(self):
        # Create new task states for tasks in reset
        self._states = {task: _OrderedTask(task) for task in self._tasks}

    @staticmethod
    def decorate_ordered(fn, state, after, reset_after):

        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            with self._reset_lock:
                if (reset_after is not None and
                        self._states[reset_after].complete):
                    self.reset_states()
            states = self._states
            log_after = kwargs.pop('log_after', DEFAULT_LOG_AFTER)
            timeout = kwargs.pop('timeout', None)
            timeout_timer = None
            if timeout is not None:
                timeout_timer = timeutils.StopWatch(duration=timeout)
                timeout_timer.start()
            if after is not None:
                states[after].wait_for_completion(state,
                                                  log_after, timeout_timer)
            states[state].run_once(lambda: fn(self, *args, **kwargs),
                                   log_after, timeout_timer)
        return wrapper


def ordered(after=None, reset_after=None):
    def _ordered(fn):
        # Set an attribute on the method so we can find it later
        setattr(fn, '_ordered', True)
        state = fn.__name__

        return _OrderedTaskRunner.decorate_ordered(fn, state, after,
                                                   reset_after)
    return _ordered


class MessageHandlingService(ServiceBase, _OrderedTaskRunner):
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

    @ordered(reset_after='stop')
    def start(self, override_pool_size=None):
        if self._started:
            LOG.warning('Restarting a MessageHandlingServer is inherently '
                        'racy. It is deprecated, and will become a noop '
                        'in a future release of oslo.messaging. If you '
                        'need to restart MessageHandlingServer you should '
                        'instantiate a new object.')
        self._started = True
        targets = [endpoint.target for endpoint in self.dispatcher.manager.endpoints]
        targets.insert(0, self.dispatcher.manager.target)
        self.listener = self.rpcdriver.listen(targets)
        self._work_pool = \
            threadgroup.ThreadGroup(self.conf.rpc_eventlet_pool_size)
        self._ioloop = eventlet.spawn(self._runner)
        LOG.info("%(class)s started" % {'class': self.__class__.__name__})

    @ordered(after='start')
    def stop(self):
        self.listener.stop()
        self._started = False

    # @excutils.forever_retry_uncaught_exceptions
    def _runner(self):
        while self._started:
            incoming = self.listener.poll()
            if incoming:
                self._submit_work(self.dispatcher(incoming))
        while True:
            incoming = self.listener.poll()
            if incoming:
                self._submit_work(self.dispatcher(incoming))
            else:
                return

    @ordered(after='stop')
    def wait(self):
        # wait all self.runner thread finish
        self._ioloop.wait()
        self._work_pool.wait()
        self.listener.cleanup()
        self.dispatcher = None
        self.rpcdriver = None

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

    def __init__(self, manager, *args, **kwargs):
        if isinstance(manager, basestring):
            self.manager = importutils.import_class(manager)(*args, **kwargs)
        else:
            self.manager = manager
        if not isinstance(manager, ManagerBase):
            raise RuntimeError('Manager type error')
        self.saved_args, self.saved_kwargs = args, kwargs
        self.timers = []
        super(LauncheRpcServiceBase, self).__init__(self.manager.__class__.__name__)
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
        LOG.info('Launche rpc service base trying stop')
        if self.messageservice is not None:
            LOG.warning('Message service started, try stop it')
            # Try to shut the connection down, but if we get any sort of
            # errors, go ahead and ignore them.. as we're shutting down anyway
            # This function will call by Launcher from outside
            try:
                self.messageservice.stop()
                self.messageservice.wait()
                LOG.info('Launche messageservice stoped')
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
        LOG.info('Launche rpc service base stoped')

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
