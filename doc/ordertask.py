
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