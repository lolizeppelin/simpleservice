from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver.impl import RabbitDriver


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


DEFAULT_LOG_AFTER = 30


class RPCClientBase(object):

    def __init__(self, conf, timeout=None, retry=None):
        self.conf = conf
        self.rpcdriver = RabbitDriver(conf)
        self.timeout = timeout or conf.rpc_send_timeout
        self.retry = retry or conf.rpc_send_retry

    def notify(self, target, ctxt, msg):
        try:
            self.rpcdriver.send_notification(target, ctxt, msg, retry=self.retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.RpcClientSendError(target, ex)

    def cast(self, target, ctxt, msg):
        """Invoke a method and return immediately. See RPCClient.cast()."""
        try:
            self.rpcdriver.send(target, ctxt, msg,
                                retry=self.retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.RpcClientSendError(target, ex)

    def call(self, target, ctxt, msg, timeout=None):
        if target.fanout:
            raise exceptions.InvalidTarget('A call cannot be used with fanout', target)
        timeout = timeout or self.timeout
        try:
            return self.rpcdriver.send(target, ctxt, msg,
                                       wait_for_reply=True, timeout=timeout,
                                       retry=self.retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.RpcClientSendError(target, ex)
