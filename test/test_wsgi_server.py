# -*- coding: UTF-8 -*-
# 控制端服务

import os

import logging as default_logging
from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice import config as base_config
from simpleservice.wsgi.config import wsgi_options
from simpleservice.server import LaunchWrapper
from simpleservice.server import launch
from simpleservice.wsgi.factory import app_factory
from simpleservice.wsgi.service import load_paste_app
from simpleservice.wsgi.service import LauncheWsgiServiceBase


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


center_group = cfg.OptGroup(name='center', title='group of center')


def configure(version=None, config_files=None):
    base_config.configure()
    base_config.set_default_for_default_log_levels(['routes=INFO', ])
    CONF(project=center_group.name, version=version,
         default_config_files=config_files)
    CONF.register_group(center_group)
    logging.setup(CONF, center_group.name)
    default_logging.captureWarnings(True)
    CONF.register_opts(wsgi_options, group=center_group)
    # 确认paste_deploy配置文件
    if not CONF[center_group.name].paste_config:
        LOG.critical('Paste config file not exist')
    if not os.path.isabs(CONF[center_group.name].paste_config):
        paste_config = CONF.find_file(CONF[center_group.name].paste_config)
    else:
        paste_config = CONF[center_group.name].paste_config
    return paste_config


def run(topdir):
    if os.path.isdir(topdir):
        config_file = os.path.join(topdir, '%s.conf' % center_group.name)
    else:
        config_file = topdir
    paste_config = configure(config_files=[config_file, ])
    app = load_paste_app(center_group, paste_config)
    servers = []
    wsgi_server = LauncheWsgiServiceBase(center_group.name, app,
                                         CONF[center_group.name].bind_ip,
                                         CONF[center_group.name].bind_port)
    wsgi_wrapper = LaunchWrapper(wsgi_server, CONF[center_group.name].wsgi_process)
    servers.append(wsgi_wrapper)
    launch(servers, CONF.user, CONF.group)


app_factory = app_factory([])


def main():
    config_file = 'C:\\Users\\loliz_000\\Desktop\\etc\\simpleservice.conf'
    run(config_file)


if __name__ == '__main__':
    main()
