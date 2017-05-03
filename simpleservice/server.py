# -*- coding: UTF-8 -*-
import os
import socket

from simpleutil.log import log as logging

from simpleutil.config import cfg

from simpleutil.service.base import ProcessLauncher
from simpleutil.service.base import ServiceLauncher
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


def launch(servers, user, group):
    if max([server.workers for server in servers]) > 1:
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
    for server in servers:
        launcher.wait()
        LOG.info('Stop the %(name)s server' %
                     {'name': server.server.name})
