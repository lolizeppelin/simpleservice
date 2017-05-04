import time
# import threading

from simpleutil.log import log as logging
from simpleutil.utils import timeutils
from simpleutil.utils import cachetools
from simpleservice.rpc.driver import common as rpc_common
from simpleservice.rpc.driver import exceptions

LOG = logging.getLogger(__name__)


class AMQPIncomingMessage(object):

    def __init__(self, listener, ctxt, message, unique_id, msg_id, reply_q,
                 obsolete_reply_queues):
        """
        message is Intance of
        simpleservice.rpc.driver.connection.RabbitMessage
        """
        self.ctxt = ctxt
        self.message = message
        self.listener = listener
        self.unique_id = unique_id
        self.msg_id = msg_id
        self.reply_q = reply_q
        self._obsolete_reply_queues = obsolete_reply_queues
        self.stopwatch = timeutils.StopWatch()
        self.stopwatch.start()

    def _send_reply(self, conn, reply=None, failure=None, log_failure=True):
        if not self._obsolete_reply_queues.reply_q_valid(self.reply_q,
                                                         self.msg_id):
            return

        if failure:
            failure = rpc_common.serialize_remote_exception(failure,
                                                            log_failure)
        # NOTE(sileht): ending can be removed in N*, see Listener.wait()
        # for more detail.
        msg = {'result': reply, 'failure': failure, 'ending': True,
               '_msg_id': self.msg_id}
        rpc_common._add_unique_id(msg)
        unique_id = msg[rpc_common.UNIQUE_ID]
        LOG.debug("sending reply msg_id: %(msg_id)s "
                  "reply queue: %(reply_q)s "
                  "time elapsed: %(elapsed)ss" %
                  {'msg_id': self.msg_id,
                   'unique_id': unique_id,
                   'reply_q': self.reply_q,
                   'elapsed': self.stopwatch.elapsed()})
        conn.direct_send(self.reply_q, rpc_common.serialize_msg(msg))

    def reply(self, reply=None, failure=None, log_failure=True):
        if not self.msg_id:
            # NOTE(Alexei_987) not sending reply, if msg_id is empty
            #    because reply should not be expected by caller side
            return

        # NOTE(sileht): return without hold the a connection if possible
        if not self._obsolete_reply_queues.reply_q_valid(self.reply_q,
                                                         self.msg_id):
            return
        # NOTE(sileht): we read the configuration value from the driver
        # to be able to backport this change in previous version that
        # still have the qpid driver
        duration = self.listener.driver.missing_destination_retry_timeout
        timer = rpc_common.DecayingTimer(duration=duration)
        timer.start()

        while True:
            try:
                with self.listener.driver._get_connection(
                        rpc_common.PURPOSE_SEND) as conn:
                    self._send_reply(conn, reply, failure,
                                     log_failure=log_failure)
                return
            except exceptions.AMQPDestinationNotFound:
                if timer.check_return() > 0:
                    LOG.debug("The reply %(msg_id)s cannot be sent  "
                               "%(reply_q)s reply queue don't exist, "
                               "retrying..." %
                              {'msg_id': self.msg_id, 'reply_q': self.reply_q})
                    time.sleep(0.25)
                else:
                    self._obsolete_reply_queues.add(self.reply_q, self.msg_id)
                    LOG.info("The reply %(msg_id)s cannot be sent "
                             "%(reply_q)s reply queue don't exist after "
                             "%(duration)s sec abandoning..." %
                             {'msg_id': self.msg_id, 'reply_q': self.reply_q, 'duration': duration})
                    return

    def acknowledge(self):
        self.message.acknowledge()
        self.listener.msg_id_cache.add(self.unique_id)

    def requeue(self):
        # NOTE(sileht): In case of the connection is lost between receiving the
        # message and requeing it, this requeue call fail
        # but because the message is not acknowledged and not added to the
        # msg_id_cache, the message will be reconsumed, the only difference is
        # the message stay at the beginning of the queue instead of moving to
        # the end.
        self.message.requeue()


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
        LOG.debug("received message msg_id: %(msg_id)s reply to %(queue)s", {
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
