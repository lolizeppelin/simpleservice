# -*- coding: UTF-8 -*-
import os
import socket

from simpleutil import system
from simpleutil.log import log as logging
from simpleutil.config import cfg

from simpleservice.config import ntp_opts
from simpleservice.base import ProcessLauncher
from simpleservice.base import ServiceLauncher
from simpleutil.posix import systemd

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class ServerWrapper(object):
    """Wraps a Server with some launching info & capabilities."""

    def __init__(self, server, workers):
        self.server = server
        self.workers = workers

    def launch_with(self, launcher):
        # self.server.listen()
        if self.workers > 1:
            # Use multi-process launcher
            launcher.launch_service(self.server, self.workers)
        else:
            # Use single process launcher
            launcher.launch_service(self.server)


def launch(servers, user='root', group='root'):
    CONF.register_opts(ntp_opts)
    if CONF.ntp_server:
        from simpleutil.utils.timeutils import ntptime
        if abs(ntptime(CONF.ntp_server, CONF.ntp_versio, CONF.ntp_port, CONF.ntp_timeout).offset) >= 1.0:
            raise RuntimeError('Ntp offset more then 1 second, Please sync time first before launch')
    if max([server.workers for server in servers]) > 1:
        if not system.POSIX:
            raise RuntimeError('ProcessLauncher just for posix system')
        launcher = ProcessLauncher(CONF)
    else:
        launcher = ServiceLauncher(CONF)
    # 根据情况启动守护进程
    systemd.daemon(pidfile=os.path.join(CONF.state_path, '%s.lock' % servers[0].server.name),
                   user=user, group=group)
    for server in servers:
        try:
            server.launch_with(launcher)
        except socket.error:
            LOG.exception('Failed to start the %(name)s server' % {
                'name': server.server.name})
            raise
    # notify calling process we are ready to serve
    systemd.notify_once()
    launcher.wait()
    for server in servers:
        LOG.info('Stoped %(name)s server' % {'name': server.server.name})
