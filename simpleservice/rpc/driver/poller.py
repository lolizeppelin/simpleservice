# import threading

from simpleutil.log import log as logging
from simpleutil.utils import cachetools
from simpleservice.rpc.driver import common as rpc_common
from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver.message import AMQPIncomingMessage

LOG = logging.getLogger(__name__)


class ObsoleteReplyQueuesCache(object):
    """Cache of reply queue id that doesn't exists anymore.

    NOTE(sileht): In case of a broker restart/failover
    a reply queue can be unreachable for short period
    the IncomingMessage.send_reply will block for 60 seconds
    in this case or until rabbit recovers.

    But in case of the reply queue is unreachable because the
    rpc client is really gone, we can have a ton of reply to send
    waiting 60 seconds.
    This leads to a starvation of connection of the pool
    The rpc server take to much time to send reply, other rpc client will
    raise TimeoutError because their don't receive their replies in time.

    This object cache stores already known gone client to not wait 60 seconds
    and hold a connection of the pool.
    Keeping 200 last gone rpc client for 1 minute is enough
    and doesn't hold to much memory.
    """

    SIZE = 200
    TTL = 60

    def __init__(self):
        # self._lock = threading.RLock()
        # TTLCache patched!
        # Default timer is timeutils.monotonic
        self._cache = cachetools.TTLCache(self.SIZE, self.TTL)

    def reply_q_valid(self, reply_q, msg_id):
        if reply_q in self._cache:
            self._no_reply_log(reply_q, msg_id)
            return False
        return True

    def add(self, reply_q, msg_id):
        # with self._lock:
        self._cache.update({reply_q: msg_id})
        self._no_reply_log(reply_q, msg_id)

    def _no_reply_log(self, reply_q, msg_id):
        LOG.warning("%(reply_queue)s doesn't exists, drop reply to %(msg_id)s" %
                    {'reply_queue': reply_q, 'msg_id': msg_id})


class AMQPListener(object):

    def __init__(self, driver, conn):

        self.prefetch_size = driver.prefetch_size
        self.driver = driver
        self.conn = conn
        self.msg_id_cache = rpc_common._MsgIdCache()
        self.incoming = []
        # self._stopped = threading.Event()
        self._stopped = False
        self._obsolete_reply_queues = ObsoleteReplyQueuesCache()

    def __call__(self, message):
        # simpleservice.rpc.driver.connection.RabbitMessage
        ctxt = rpc_common.unpack_context(message)
        unique_id = self.msg_id_cache.check_duplicate_message(message)
        LOG.debug("received message msg_id: %(msg_id)s reply to %(queue)s" % {
            'queue': ctxt.reply_q, 'msg_id': ctxt.msg_id})
        self.incoming.append(AMQPIncomingMessage(self,
                                                 ctxt.to_dict(),
                                                 message,
                                                 unique_id,
                                                 ctxt.msg_id,
                                                 ctxt.reply_q,
                                                 self._obsolete_reply_queues))

    # @base.batch_poll_helper
    def poll(self, timeout=None):
        # while not self._stopped.is_set():
        while not self._stopped:
            if self.incoming:
                return self.incoming.pop(0)
            try:
                self.conn.consume(timeout=timeout)
            except exceptions.Timeout:
                return None

    def stop(self):
        # self._stopped.set()
        self._stopped = True
        self.conn.stop_consuming()

    def cleanup(self):
        # Closes listener connection
        self.conn.close()
