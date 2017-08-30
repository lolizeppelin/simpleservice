from simpleutil.config import cfg
from simpleutil.log import log as logging

from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver.impl import RabbitDriver


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class RPCClientBase(object):

    def __init__(self, conf):
        self.conf = conf
        self.rpcdriver = RabbitDriver(conf)

    def notify(self, target, ctxt, msg):
        try:
            self.rpcdriver.send_notification(target, ctxt, msg, retry=self.conf.rabbit_send_retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.RpcClientSendError(target, ex)

    def cast(self, target, ctxt, msg):
        """Invoke a method and return immediately. See RPCClient.cast()."""
        try:
            self.rpcdriver.send(target, ctxt, msg, timeout=self.conf.rpc_send_timeout,
                                retry=self.conf.rpc_send_retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.RpcClientSendError(target, ex)

    def call(self, target, ctxt, msg, timeout=None):
        if target.fanout:
            raise exceptions.InvalidTarget('A call cannot be used with fanout', target)
        try:
            return self.rpcdriver.send(target, ctxt, msg,
                                       wait_for_reply=True,
                                       timeout=timeout if timeout else self.conf.rpc_send_timeout,
                                       retry=self.conf.rpc_send_retry)
        except exceptions.RabbitDriverError as ex:
            raise exceptions.RpcClientSendError(target, ex)
