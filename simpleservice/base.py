# -*- coding: UTF-8 -*-
import abc
import collections
import errno
import io
import os
import random
import signal
import sys
import time
import six

import eventlet
import eventlet.hubs
from eventlet import event
from eventlet.greenio import GreenPipe


from simpleutil.log import log as logging
from simpleutil.utils import singleton
from simpleutil.utils import threadgroup
from simpleutil.utils import uuidutils
from simpleutil.utils import systemutils
from simpleutil.utils import systemdutils
from simpleservice.config import service_opts
from simpleservice.plugin import exceptions
if systemutils.LINUX:
    from simpleutil.utils.systemutils import posix
    from simpleutil.utils.systemutils.posix import linux


LOG = logging.getLogger(__name__)

SnowflakeId = 0


def _check_service_base(service):
    if not isinstance(service, ServiceBase):
        raise TypeError("Service %(service)s must an instance of %(base)s!"
                        % {'service': service, 'base': ServiceBase})


def _check_launch_service_base(service):
    if not isinstance(service, LauncheServiceBase):
        raise TypeError("Service %(service)s must an instance of %(base)s!"
                        % {'service': service, 'base': LauncheServiceBase})
    if systemutils.LINUX:
        if not linux.user_exist(service.user) or not linux.group_exist(service.group):
            raise RuntimeError('Run user or group not exist')


def _is_daemon():
    # The process group for a foreground process will match the
    # process group of the controlling terminal. If those values do
    # not match, or ioctl() fails on the stdout file handle, we assume
    # the process is running in the background as a daemon.
    # http://www.gnu.org/software/bash/manual/bashref.html#Job-Control-Basics
    # 判断是否进程在后台运行
    try:
        is_daemon = os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno())
    except io.UnsupportedOperation:
        # Could not get the fileno for stdout, so we must be a daemon.
        is_daemon = True
    except OSError as err:
        if err.errno == errno.ENOTTY:
            # Assume we are a daemon because there is no terminal.
            is_daemon = True
        else:
            raise
    return is_daemon


def _is_sighup_and_daemon(signo):
    if not (SignalHandler().is_signal_supported('SIGHUP') and
            signo == signal.SIGHUP):
        # Avoid checking if we are a daemon, because the signal isn't
        # SIGHUP.
        return False
    return _is_daemon()


class SignalExit(SystemExit):
    def __init__(self, signo, exccode=1):
        super(SignalExit, self).__init__(exccode)
        self.signo = signo


@six.add_metaclass(abc.ABCMeta)
class ServiceBase(object):
    """Base class for all services."""

    @abc.abstractmethod
    def start(self):
        """Start service."""

    @abc.abstractmethod
    def stop(self):
        """Stop service."""

    @abc.abstractmethod
    def wait(self):
        """Wait for service to complete."""

    @abc.abstractmethod
    def reset(self):
        """Reset service.

        Called in case service running in daemon mode receives SIGHUP.
        """


class LauncheServiceBase(ServiceBase):
    """ServiceBase for Launche"""

    def __init__(self, name, user='root', group='root',
                 plugin_threadpool=None):
        self.name = name
        self.user = user
        self.group = group
        self.plugin_threadpool = plugin_threadpool

    def close_exec(self):
        """set  close_exec here"""


class Services(object):

    def __init__(self):
        self.services = []
        self.tg = threadgroup.ThreadGroup()
        self.done = event.Event()

    def add(self, service):
        """Add a service to a list and create a thread to run it.

        :param service: service to run
        """
        self.services.append(service)
        self.tg.add_thread(self.run_service, service, self.done)

    def stop(self):
        """Wait for graceful shutdown of services and kill the threads."""
        for service in self.services:
            service.stop()

        # Each service has performed cleanup, now signal that the run_service
        # wrapper threads can now die:
        if not self.done.ready():
            self.done.send()

        # reap threads:
        self.tg.stop()

    def wait(self):
        """Wait for services to shut down."""
        for service in self.services:
            service.wait()
        self.tg.wait()

    def restart(self):
        """Reset services and start them in new threads."""
        self.stop()
        self.done = event.Event()
        for restart_service in self.services:
            restart_service.reset()
            self.tg.add_thread(self.run_service, restart_service, self.done)

    @staticmethod
    def run_service(service, done):
        """Service start wrapper.

        :param service: service to run
        :param done: event to wait on until a shutdown is triggered
        :returns: None

        """
        try:
            service.start()
        except Exception as e:
            if isinstance(e, exceptions.AfterRequestError):
                LOG.error('Http request error: %s' % e.message)
                LOG.error('Http status code %d, error msg %s' % (e.code, e.resone))
            LOG.exception('Error starting a service.')
            raise SystemExit(1)
        else:
            done.wait()


class ServiceWrapper(object):
    def __init__(self, service, workers):
        self.service = service
        self.workers = workers
        self.children = set()
        self.forktimes = []
        # for snowflaked id
        self.free_snowflakeid = set()
        for i in xrange(1, 256):
            self.free_snowflakeid.add(i)
        self.snowflakeid_map = dict()

    def per_set_snowflake_pid(self):
        global SnowflakeId
        while True:
            try:
                SnowflakeId = self.free_snowflakeid.pop()
                break
            except KeyError:
                time.sleep(0.5)

    def post_set_snowflake_pid(self, pid):
        global SnowflakeId
        self.snowflakeid_map[pid] = SnowflakeId
        SnowflakeId = 0

    def free_snowflake_pid(self, pid):
        try:
            self.free_snowflakeid.add(self.snowflakeid_map.pop(pid))
        except KeyError:
            LOG.warning('pid %d not in snowflake id map list', pid)


@singleton.singleton
class SignalHandler(object):

    def __init__(self, *args, **kwargs):
        super(SignalHandler, self).__init__(*args, **kwargs)
        # Map all signal names to signal integer values and create a
        # reverse mapping (for easier + quick lookup).
        self._ignore_signals = ('SIG_DFL', 'SIG_IGN')
        self._signals_by_name = dict((name, getattr(signal, name))
                                     for name in dir(signal)
                                     if name.startswith("SIG")
                                     and name not in self._ignore_signals)
        self.signals_to_name = dict(
            (sigval, name)
            for (name, sigval) in self._signals_by_name.items())
        self._signal_handlers = collections.defaultdict(set)
        self.clear()

    def clear(self):
        for sig in self._signal_handlers:
            signal.signal(sig, signal.SIG_DFL)
        self._signal_handlers.clear()

    def add_handlers(self, signals, handler):
        for sig in signals:
            self.add_handler(sig, handler)

    def add_handler(self, sig, handler):
        if not self.is_signal_supported(sig):
            return
        signo = self._signals_by_name[sig]
        self._signal_handlers[signo].add(handler)
        signal.signal(signo, self._handle_signal)

    def _handle_signal(self, signo, frame):
        # This method can be called anytime, even between two Python
        # instructions. It's scheduled by the C signal handler of Python using
        # Py_AddPendingCall().
        #
        # We only do one thing: schedule a call to _handle_signal_cb() later.
        # eventlet.spawn() is not signal-safe: _handle_signal() can be called
        # during a call to eventlet.spawn(). This case is supported, it is
        # ok to schedule multiple calls to _handle_signal() with the same
        # signal number.
        #
        # To call to _handle_signal_cb() is delayed to avoid reentrant calls to
        # _handle_signal_cb(). It avoids race conditions like reentrant call to
        # clear(): clear() is not reentrant (bug #1538204).
        eventlet.spawn(self._handle_signal_cb, signo, frame)

    def _handle_signal_cb(self, signo, frame):
        for handler in self._signal_handlers[signo]:
            handler(signo, frame)

    def is_signal_supported(self, sig_name):
        return sig_name in self._signals_by_name


class Launcher(object):
    """Launch one or more services and wait for them to complete."""

    def __init__(self, conf):
        """Initialize the service launcher.

        :returns: None

        """
        self.conf = conf
        conf.register_opts(service_opts)
        self.services = Services()

    def launch_service(self, service):
        """Load and start the given service.

        :param service: The service you would like to start, must be an
                        instance of :class:`oslo_service.service.ServiceBase`
        :returns: None

        """
        _check_launch_service_base(service)
        if systemutils.LINUX:
            linux.drop_privileges(user=service.user, group=service.group)
            systemutils.PID = os.getpid()
        self.services.add(service)

    def stop(self):
        """Stop all services which are currently running.

        :returns: None

        """
        self.services.stop()

    def wait(self):
        """Wait until all services have been stopped, and then return.

        :returns: None

        """
        self.services.wait()

    def restart(self):
        """Reload config files and restart service.

        :returns: None

        """
        self.conf.reload_config_files()
        self.services.restart()


class ServiceLauncher(Launcher):
    """Runs one or more service in a parent process."""
    def __init__(self, conf):
        """Constructor.

        :param conf: an instance of ConfigOpts
        """
        super(ServiceLauncher, self).__init__(conf)
        self.signal_handler = SignalHandler()

    def _graceful_shutdown(self, *args):
        self.signal_handler.clear()
        if (self.conf.graceful_shutdown_timeout and
                self.signal_handler.is_signal_supported('SIGALRM')):
            signal.alarm(self.conf.graceful_shutdown_timeout)
        self.stop()

    def _reload_service(self, *args):
        self.signal_handler.clear()
        raise SignalExit(signal.SIGHUP)

    def _fast_exit(self, *args):
        LOG.info('Caught SIGINT signal, instantaneous exiting')
        os._exit(1)

    def _on_timeout_exit(self, *args):
        LOG.info('Graceful shutdown timeout exceeded, '
                     'instantaneous exiting')
        os._exit(1)

    def handle_signal(self):
        """Set self._handle_signal as a signal handler."""
        self.signal_handler.add_handler('SIGTERM', self._graceful_shutdown)
        self.signal_handler.add_handler('SIGINT', self._fast_exit)
        self.signal_handler.add_handler('SIGHUP', self._reload_service)
        self.signal_handler.add_handler('SIGALRM', self._on_timeout_exit)

    def _wait_for_exit_or_signal(self):
        status = None
        signo = 0
        if self.conf.log_options:
            LOG.debug('Full set of CONF:')
            self.conf.log_opt_values(LOG, logging.DEBUG)

        try:
            super(ServiceLauncher, self).wait()
        except SignalExit as exc:
            signame = self.signal_handler.signals_to_name[exc.signo]
            LOG.info('Caught %s, exiting'), signame
            status = exc.code
            signo = exc.signo
        except SystemExit as exc:
            self.stop()
            status = exc.code
        except Exception:
            LOG.exception('wait service launcher error')
            self.stop()
        return status, signo

    def wait(self):
        """Wait for a service to terminate and restart it on SIGHUP.

        :returns: termination status
        """
        systemdutils.notify_once()
        self.signal_handler.clear()
        while True:
            self.handle_signal()
            status, signo = self._wait_for_exit_or_signal()
            if not _is_sighup_and_daemon(signo):
                break
            self.restart()
        return status


class ProcessLauncher(object):
    """Launch a service with a given number of workers."""

    def __init__(self, conf, wait_interval=0.01):
        """Constructor.

        :param conf: an instance of ConfigOpts
        :param wait_interval: The interval to sleep for between checks
                              of child process exit.
        """
        self.conf = conf
        conf.register_opts(service_opts)
        self.children = {}
        self.sigcaught = None
        self.running = True
        self.wait_interval = wait_interval
        self.launcher = None
        rfd, self.writepipe = os.pipe()
        # self.readpipe = eventlet.greenio.GreenPipe(rfd, 'r')
        self.readpipe = GreenPipe(rfd, 'r')
        self.signal_handler = SignalHandler()
        self.handle_signal()

    def handle_signal(self):
        """Add instance's signal handlers to class handlers."""
        self.signal_handler.add_handlers(('SIGTERM', 'SIGHUP'),
                                         self._handle_signal)
        self.signal_handler.add_handler('SIGINT', self._fast_exit)
        self.signal_handler.add_handler('SIGALRM', self._on_alarm_exit)

    def _handle_signal(self, signo, frame):
        """Set signal handlers.

        :param signo: signal number
        :param frame: current stack frame
        """
        self.sigcaught = signo
        self.running = False

        # Allow the process to be killed again and die from natural causes
        self.signal_handler.clear()

    def _fast_exit(self, signo, frame):
        LOG.info('Caught SIGINT signal, instantaneous exiting')
        os._exit(1)

    def _on_alarm_exit(self, signo, frame):
        LOG.info('Graceful shutdown timeout exceeded, '
                     'instantaneous exiting')
        os._exit(1)

    def _pipe_watcher(self):
        # This will block until the write end is closed when the parent
        # dies unexpectedly
        self.readpipe.read(1)

        LOG.info('Parent process has died unexpectedly, exiting')

        if self.launcher:
            self.launcher.stop()
        sys.exit(1)

    def _child_process_handle_signal(self):
        # Setup child signal handlers differently

        def _sigterm(*args):
            self.signal_handler.clear()
            LOG.info('Get sigterm, pid:%d' % os.getpid())
            self.launcher.stop()

        def _sighup(*args):
            self.signal_handler.clear()
            raise SignalExit(signal.SIGHUP)

        self.signal_handler.clear()

        # Parent signals with SIGTERM when it wants us to go away.
        self.signal_handler.add_handler('SIGTERM', _sigterm)
        self.signal_handler.add_handler('SIGHUP', _sighup)
        self.signal_handler.add_handler('SIGINT', self._fast_exit)

    def _child_wait_for_exit_or_signal(self, launcher):
        status = 0
        signo = 0

        # NOTE(johannes): All exceptions are caught to ensure this
        # doesn't fallback into the loop spawning children. It would
        # be bad for a child to spawn more children.
        try:
            launcher.wait()
        except SignalExit as exc:
            signame = self.signal_handler.signals_to_name[exc.signo]
            LOG.info('Child caught %s, exiting', signame)
            status = exc.code
            signo = exc.signo
        except SystemExit as exc:
            status = exc.code
        except BaseException:
            LOG.exception('Unhandled exception')
            status = 2

        return status, signo

    def _child_process(self, service):
        self._child_process_handle_signal()

        # Reopen the eventlet hub to make sure we don't share an epoll
        # fd with parent and/or siblings, which would be bad
        eventlet.hubs.use_hub()

        # Close write to ensure only parent has it open
        os.close(self.writepipe)
        # Create greenthread to watch for parent to close pipe
        eventlet.spawn_n(self._pipe_watcher)

        # Reseed random number generator
        random.seed()

        launcher = Launcher(self.conf)
        launcher.launch_service(service)
        return launcher

    def _start_child(self, wrap):
        if len(wrap.forktimes) > wrap.workers:
            # Limit ourselves to one process a second (over the period of
            # number of workers * 1 second). This will allow workers to
            # start up quickly but ensure we don't fork off children that
            # die instantly too quickly.
            if time.time() - wrap.forktimes[0] < wrap.workers:
                LOG.info('Forking too fast, sleeping')
                time.sleep(1)
            wrap.forktimes.pop(0)
        wrap.forktimes.append(time.time())

        wrap.per_set_snowflake_pid()

        pid = os.fork()
        if pid == 0:
            # set cloexec to readpipe
            systemutils.set_cloexec_flag(self.readpipe.fileno())
            uuidutils.Gkey.update_pid(SnowflakeId)
            self.launcher = self._child_process(wrap.service)
            # while True:
            #     self._child_process_handle_signal()
            #     status, signo = self._child_wait_for_exit_or_signal(
            #         self.launcher)
            #     if not _is_sighup_and_daemon(signo):
            #         break
            #     self.launcher.restart()
            self._child_process_handle_signal()
            status, signo = self._child_wait_for_exit_or_signal(self.launcher)
            os._exit(status)

        LOG.debug('Started child %d', pid)

        wrap.post_set_snowflake_pid(pid)

        wrap.children.add(pid)
        self.children[pid] = wrap
        return pid

    def launch_service(self, service, workers=1):
        """Launch a service with a given number of workers.

       :param service: a service to launch, must be an instance of
              :class:`oslo_service.service.ServiceBase`
       :param workers: a number of processes in which a service
              will be running
        """
        _check_launch_service_base(service)
        wrap = ServiceWrapper(service, workers)

        LOG.info('Starting %d workers', wrap.workers)
        while self.running and len(wrap.children) < wrap.workers:
            self._start_child(wrap)

    def _wait_child(self):
        try:
            # Don't block if no child processes have exited
            pid, status = os.waitpid(0, os.WNOHANG)
            if not pid:
                return None
        except OSError as exc:
            if exc.errno not in (errno.EINTR, errno.ECHILD):
                raise
            return None

        if os.WIFSIGNALED(status):
            sig = os.WTERMSIG(status)
            LOG.info('Child %(pid)d killed by signal %(sig)d',
                     dict(pid=pid, sig=sig))
        else:
            code = os.WEXITSTATUS(status)
            LOG.info('Child %(pid)s exited with status %(code)d',
                     dict(pid=pid, code=code))

        if pid not in self.children:
            LOG.warning('pid %d not in child list', pid)
            return None

        wrap = self.children.pop(pid)
        wrap.children.remove(pid)
        # free snowflake pid
        wrap.free_snowflake_pid(pid)
        return wrap

    def _respawn_children(self):
        while self.running:
            wrap = self._wait_child()
            if not wrap:
                # Yield to other threads if no children have exited
                # Sleep for a short time to avoid excessive CPU usage
                # (see bug #1095346)
                eventlet.greenthread.sleep(self.wait_interval)
                continue
            while self.running and len(wrap.children) < wrap.workers:
                self._start_child(wrap)
        LOG.debug('Spawn children thread stop')

    def wait(self):
        """Loop waiting on children to die and respawning as necessary."""

        systemdutils.notify_once()
        if self.conf.log_options:
            LOG.debug('Full set of CONF:')
            self.conf.log_opt_values(LOG, logging.DEBUG)

        try:
            while True:
                self.handle_signal()
                self._respawn_children()
                # No signal means that stop was called.  Don't clean up here.
                if not self.sigcaught:
                    return

                signame = self.signal_handler.signals_to_name[self.sigcaught]
                LOG.info('Caught %s, stopping children', signame)
                if not _is_sighup_and_daemon(self.sigcaught):
                    break

                self.conf.reload_config_files()
                for service in set(
                        [wrap.service for wrap in self.children.values()]):
                    service.reset()

                for pid in self.children:
                    os.kill(pid, signal.SIGTERM)

                self.running = True
                self.sigcaught = None
        except eventlet.greenlet.GreenletExit:
            LOG.info("Wait called after thread killed. Cleaning up.")

        # if we are here it means that we are trying to do graceful shutdown.
        # add alarm watching that graceful_shutdown_timeout is not exceeded
        if (self.conf.graceful_shutdown_timeout and
                self.signal_handler.is_signal_supported('SIGALRM')):
            signal.alarm(self.conf.graceful_shutdown_timeout)

        self.stop()

    def stop(self):
        """Terminate child processes and wait on each."""
        self.running = False

        LOG.debug("Stop services.")
        for service in set(
                [wrap.service for wrap in self.children.values()]):
            service.stop()

        LOG.debug("Killing children. pid:%d" % os.getpid())
        for pid in self.children:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError as exc:
                if exc.errno != errno.ESRCH:
                    LOG.error('Killing catch unexpecte errno: %d' % exc.errno)
                    raise

        # Wait for children to die
        if self.children:
            LOG.info('Waiting on %d children to exit', len(self.children))
            while self.children:
                self._wait_child()
