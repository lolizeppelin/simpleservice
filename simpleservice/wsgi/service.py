import os
import socket


import eventlet
import eventlet.wsgi
import greenlet

from paste import deploy

from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice.base import LauncheServiceBase

from simpleutil.common.exceptions import InvalidInput
from simpleservice.wsgi.exceptions import ConfigNotFound
from simpleservice.wsgi.exceptions import PasteAppNotFound


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


wsgi_opts = [
    cfg.StrOpt('wsgi_log_format',
               default='%(client_ip)s "%(request_line)s" status: '
                       '%(status_code)s  len: %(body_length)s time:'
                       ' %(wall_seconds).7f',
               help='A python format string that is used as the template to '
                    'generate log lines. The following values can be'
                    'formatted into it: client_ip, date_time, request_line, '
                    'status_code, body_length, wall_seconds.'),
    cfg.IntOpt('tcp_keepidle',
               default=600,
               help="Sets the value of TCP_KEEPIDLE in seconds for each "
                    "server socket. Not supported on OS X."),
    cfg.IntOpt('wsgi_default_pool_size',
               default=100,
               help="Size of the pool of greenthreads used by wsgi"),
    cfg.IntOpt('max_header_line',
               default=16384,
               help="Maximum line size of message headers to be accepted. "
                    "max_header_line may need to be increased when using "
                    "large tokens (typically those generated when keystone "
                    "is configured to use PKI tokens with big service "
                    "catalogs)."),
    cfg.BoolOpt('wsgi_keep_alive',
                default=True,
                help="If False, closes the client socket connection "
                     "explicitly."),
    cfg.IntOpt('client_socket_timeout', default=900,
               help="Timeout for client connections' socket operations. "
                    "If an incoming connection is idle for this number of "
                    "seconds it will be closed. A value of '0' means "
                    "wait forever."),
    ]


class Loader(object):
    """Used to load WSGI applications from paste configurations."""

    def __init__(self, conf, paste_config):
        """Initialize the loader, and attempt to find the config.

        :param conf: Application config
        :returns: None

        """
        conf.register_opts(wsgi_opts)
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


def load_paste_app(app_name, paste_config):
    loader = Loader(CONF, paste_config)
    app = loader.load_app(app_name)
    return app


class LauncheWsgiServiceBase(LauncheServiceBase):
    """Server class to manage a WSGI server, serving a WSGI application."""
    def __init__(self, name, app, host='0.0.0.0', port=0,  # nosec
                 backlog=128, max_url_len=None,
                 socket_family=None, socket_file=None, socket_mode=None):
        """Initialize, but do not start, a WSGI server.
        :param name: Pretty name for logging.
        :param app: The WSGI application to serve.
        :param host: IP address to serve the application.
        :param port: Port number to server the application.
        :param backlog: Maximum number of queued connections.
        :param max_url_len: Maximum length of permitted URLs.
        :param socket_family: Socket family.
        :param socket_file: location of UNIX socket.
        :param socket_mode: UNIX socket mode.
        :returns: None
        :raises: InvalidInput
        :raises: EnvironmentError
        """
        eventlet.wsgi.MAX_HEADER_LINE = CONF.max_header_line
        self.name = name
        self.app = app
        self._server = None
        self._protocol = eventlet.wsgi.HttpProtocol
        self.pool_size = CONF.wsgi_default_pool_size
        self._pool = eventlet.GreenPool(self.pool_size)
        self._logger = logging.getLogger('goperation.service.WsgiServiceBase')
        self._max_url_len = max_url_len
        self.client_socket_timeout = CONF.client_socket_timeout or None

        if backlog < 1:
            raise InvalidInput('The backlog must be more than 0')

        if not socket_family or socket_family in [socket.AF_INET,
                                                  socket.AF_INET6]:
            self.socket = self._get_socket(host, port, backlog)
        elif hasattr(socket, "AF_UNIX") and socket_family == socket.AF_UNIX:
            self.socket = self._get_unix_socket(socket_file, socket_mode,
                                                backlog)
        else:
            raise ValueError("Unsupported socket family: %s", socket_family)

        (self.host, self.port) = self.socket.getsockname()[0:2]
        LauncheServiceBase.__init__(self, name)

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
        LOG.info("%(name)s listening on %(host)s:%(port)s",
                 {'name': self.name, 'host': host, 'port': port})
        return sock

    def _get_unix_socket(self, socket_file, socket_mode, backlog):
        sock = eventlet.listen(socket_file, family=socket.AF_UNIX,
                               backlog=backlog)
        if socket_mode is not None:
            os.chmod(socket_file, socket_mode)
        LOG.info("%(name)s listening on %(socket_file)s:",
                 {'name': self.name, 'socket_file': socket_file})
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

        wsgi_kwargs = {
            'func': eventlet.wsgi.server,
            'sock': self.dup_socket,
            'site': self.app,
            'protocol': self._protocol,
            'custom_pool': self._pool,
            'log': self._logger,
            'log_format': CONF.wsgi_log_format,
            'debug': False,
            'keepalive': cfg.CONF.wsgi_keep_alive,
            'socket_timeout': self.client_socket_timeout
            }

        if self._max_url_len:
            wsgi_kwargs['url_length_limit'] = self._max_url_len

        self._server = eventlet.spawn_n(**wsgi_kwargs)

    def _set_socket_opts(self, _socket):
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # sockets can hang around forever without keepalive
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        # This option isn't available in the OS X version of eventlet
        if hasattr(socket, 'TCP_KEEPIDLE'):
            _socket.setsockopt(socket.IPPROTO_TCP,
                               socket.TCP_KEEPIDLE,
                               CONF.tcp_keepidle)

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
        LOG.info("Stopping WSGI server.")

        if self._server is not None:
            # let eventlet close socket
            self._pool.resize(0)
            self._server.kill()

    def wait(self):
        """Block, until the server has stopped.

        Waits on the server's eventlet to finish, then returns.

        :returns: None

        """
        try:
            if self._server is not None:
                num = self._pool.running()
                LOG.debug("Waiting WSGI server to finish %d requests.", num)
                self._pool.waitall()
        except greenlet.GreenletExit:
            LOG.info("WSGI server has stopped.")
