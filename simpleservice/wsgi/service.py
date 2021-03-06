# -*- coding:utf-8 -*-
import os
import socket

import eventlet
import eventlet.wsgi

from paste import deploy

from simpleutil.utils import systemutils
from simpleutil.config import cfg
from simpleutil.log import log as logging
from simpleutil.common.exceptions import InvalidInput

from simpleservice import common
from simpleservice.base import LauncheServiceBase
from simpleservice.wsgi.exceptions import ConfigNotFound
from simpleservice.wsgi.exceptions import PasteAppNotFound

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class Loader(object):
    """Used to load WSGI applications from paste configurations."""

    def __init__(self, conf, paste_config):
        """Initialize the loader, and attempt to find the config.

        :param conf: Application config
        :returns: None

        """
        if not os.path.isabs(paste_config):
            self.config_path = conf.find_file(paste_config)
        elif os.path.exists(paste_config):
            self.config_path = paste_config
        if not self.config_path:
            raise ConfigNotFound(path=paste_config)

    def load_app(self, name):
        """Return the paste URLMap wrapped WSGI application.

        :param name: Name of the application to load.
        :returns: Paste URLMap object wrapping the requested application.
        :raises: PasteAppNotFound

        """
        try:
            LOG.debug("Loading app %(name)s from %(path)s",
                      {'name': name, 'path': self.config_path})
            return deploy.loadapp("config:%s" % self.config_path, name=name)
        except LookupError:
            LOG.exception("Couldn't lookup app: %s"), name
            raise PasteAppNotFound(name=name, path=self.config_path)


def load_paste_app(name, paste_config):
    loader = Loader(name, paste_config)
    app = loader.load_app(name)
    return app


class FixedHttpProtocol(eventlet.wsgi.HttpProtocol):

    XREALIP = False

    if not systemutils.PY27:
        def __init__(self, request, client_address, server):
            """Fix bug for python2.6"""
            self.request = request
            self.client_address = client_address
            self.server = server
            self.setup()
            try:
                self.handle()
            finally:
                self.finish()

    def get_environ(self):
        """
        使用X-Real-IP头判断来源IP, 一般在使用Nginx做前端代理的情况下用
        """
        env = eventlet.wsgi.HttpProtocol.get_environ(self)
        env[common.ADMINAPI] = False
        if self.XREALIP and self.headers.get('x-real-ip'):
            env[common.GOPCLIENTIP] = self.headers.get('x-real-ip')
        else:
            env[common.GOPCLIENTIP] = self.client_address[0]
        return env


class LauncheWsgiServiceBase(LauncheServiceBase):
    """Server class to manage a WSGI server, serving a WSGI application."""
    def __init__(self, name, app, backlog=128, max_url_len=None, **kwargs):
        """Initialize, but do not start, a WSGI server.
        :param name: Pretty name for logging.
        :param app: The WSGI application to serve.
        :param backlog: Maximum number of queued connections.
        :param max_url_len: Maximum length of permitted URLs.
        :param plugin_threadpool: external thread pool need to stop
        :returns: None
        :raises: InvalidInput
        :raises: EnvironmentError
        """
        self.name = name
        self.app = app
        self.conf = CONF[name]

        socket_file = self.conf.unix_socket_file
        if systemutils.LINUX and socket_file and hasattr(socket, "AF_UNIX") :
            socket_family = socket.AF_UNIX
            socket_mode = 0o666
        else:
            socket_family = socket.AF_INET
            socket_mode= None

        self._server = None
        eventlet.wsgi.MAX_HEADER_LINE = self.conf.max_header_line
        if self.conf.x_real_ip:
            FixedHttpProtocol.XREALIP = True
        self._protocol = FixedHttpProtocol
        self.pool_size = self.conf.wsgi_default_pool_size
        self._pool = eventlet.GreenPool(self.pool_size)
        # self._logger = logging.getLogger('goperation.service.WsgiServiceBase')
        # self._logger = LOG
        self._max_url_len = max_url_len
        self.client_socket_timeout = self.conf.client_socket_timeout or None

        if backlog < 1:
            raise InvalidInput('The backlog must be more than 0')

        if socket_family in [socket.AF_INET, socket.AF_INET6]:
            self.socket = self._get_socket(self.conf.bind_ip or '0.0.0.0',
                                           self.conf.bind_port or 7999,
                                           backlog)
        elif socket_family == socket.AF_UNIX:
            self.socket = self._get_unix_socket(socket_file, socket_mode, backlog)
        else:
            raise ValueError("Unsupported socket family: %s", socket_family)
        self.dup_socket = None

        (self.host, self.port) = self.socket.getsockname()[0:2]
        plugin_threadpool = kwargs.pop('plugin_threadpool', None)
        super(LauncheWsgiServiceBase, self).__init__(name,
                                                     user=self.conf.wsgi_user,
                                                     group=self.conf.wsgi_group,
                                                     plugin_threadpool=plugin_threadpool)

    def _get_socket(self, host, port, backlog):
        bind_addr = (host, port)
        try:
            info = socket.getaddrinfo(bind_addr[0],
                                      bind_addr[1],
                                      socket.AF_UNSPEC,
                                      socket.SOCK_STREAM)[0]
            family = info[0]
            bind_addr = info[-1]
        except Exception:
            family = socket.AF_INET
        try:
            sock = eventlet.listen(bind_addr, family, backlog=backlog)
        except EnvironmentError:
            LOG.error("Could not bind to %(host)s:%(port)s",
                      {'host': host, 'port': port})
            raise
        sock = self._set_socket_opts(sock)
        # LOG.debug("%(name)s listening on %(host)s:%(port)s", {'name': self.name, 'host': host, 'port': port})
        return sock

    def _get_unix_socket(self, socket_file, socket_mode, backlog):
        sock = eventlet.listen(socket_file, family=socket.AF_UNIX,
                               backlog=backlog)
        if socket_mode is not None:
            os.chmod(socket_file, socket_mode)
        # LOG.debug("%(name)s listening on %(socket_file)s:", {'name': self.name, 'socket_file': socket_file})
        return sock

    def start(self):
        """Start serving a WSGI application.

        :returns: None
        """
        # The server socket object will be closed after server exits,
        # but the underlying file descriptor will remain open, and will
        # give bad file descriptor error. So duplicating the socket object,
        # to keep file descriptor usable.

        self.dup_socket = self.socket.dup()
        # set close exec to  dup_socket and socket
        self.close_exec()

        wsgi_kwargs = {
            'func': eventlet.wsgi.server,
            'sock': self.dup_socket,
            'site': self.app,
            'protocol': self._protocol,
            'custom_pool': self._pool,
            # 'log': self._logger,
            'log': logging.getLogger('eventlet.wsgi'),
            'log_format': self.conf.wsgi_log_format,
            'debug': False,
            'keepalive': self.conf.wsgi_keep_alive,
            'socket_timeout': self.client_socket_timeout
            }

        if self._max_url_len:
            wsgi_kwargs['url_length_limit'] = self._max_url_len

        self._server = eventlet.spawn(**wsgi_kwargs)

    def _set_socket_opts(self, _socket):
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sockets can hang around forever without keepalive
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # This option isn't available in the OS X version of eventlet
        if hasattr(socket, 'TCP_KEEPIDLE'):
            _socket.setsockopt(socket.IPPROTO_TCP,
                               socket.TCP_KEEPIDLE,
                               self.conf.tcp_keepidle)

        return _socket

    def reset(self):
        """Reset server greenpool size to default.

        :returns: None

        """
        self._pool.resize(self.pool_size)

    def stop(self):
        """Stops eventlet server. Doesn't allow accept new connecting.

        :returns: None

        """
        LOG.info("Stopping WSGI server.pid:%d" % os.getpid())

        if self._server is not None:
            num = self._pool.running()
            LOG.debug("Waiting WSGI server to finish %d requests.", num)
            # let eventlet close socket
            self._pool.resize(0)
            eventlet.wsgi.is_accepting = False

        if self.plugin_threadpool:
            self.plugin_threadpool.stop(graceful=True)

    def wait(self):
        if self._server is not None:
            self._server.wait()
        self._server = None

    def close_exec(self):
        if self.dup_socket:
            systemutils.set_cloexec_flag(self.dup_socket.fileno())
        systemutils.set_cloexec_flag(self.socket.fileno())
