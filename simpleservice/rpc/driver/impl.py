import uuid
# import threading
import eventlet
import eventlet.semaphore

# from six import moves

from simpleutil.log import log as logging

from simpleservice.rpc.driver import connection
from simpleservice.rpc.driver import poller
from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.driver import common as rpc_common

from simpleservice.plugin.models import MsgTimeoutRecord

from simpleutil.utils.uuidutils import Gkey
from simpleutil.utils.timeutils import realnow

LOG = logging.getLogger(__name__)


class ReplyWaiters(object):

    WAKE_UP = object()

    def __init__(self, reply_q):
        self._queues = {}
        self._wrn_threshold = 10
        self.reply_q = reply_q

    def get(self, msg_id, timeout):
        try:
            return self._queues[msg_id].get(block=True, timeout=timeout)
        # except moves.queue.Empty:
        except eventlet.queue.Empty:
            raise exceptions.MessagingTimeout(
                'Timed out waiting for a reply '
                'to message ID %s' % msg_id)

    def put(self, msg_id, message_data):
        queue = self._queues.get(msg_id)
        if not queue:
            LOG.info('No calling threads waiting for msg_id : %s' % msg_id)
            LOG.debug('queues: %(queues)s, message: %(message)s' %
                      {'queues': len(self._queues), 'message': message_data})
            if rpc_common.MsgTimeoutRecorder is not None:
                rpc_common.MsgTimeoutRecorder(msg_id, self.reply_q, message_data)
        else:
            queue.put(message_data)

    def add(self, msg_id):
        # Do not use moves.queue.Queue
        # self._queues[msg_id] = moves.queue.Queue()
        self._queues[msg_id] = eventlet.queue.Queue()
        if len(self._queues) > self._wrn_threshold:
            LOG.warning('Number of call queues is greater than warning '
                        'threshold: %(old_threshold)s. There could be a '
                        'leak. Increasing threshold to: %(threshold)s' %
                        {'old_threshold': self._wrn_threshold,
                         'threshold': self._wrn_threshold * 2})
            self._wrn_threshold *= 2

    def remove(self, msg_id):
        del self._queues[msg_id]


class ReplyWaiter(object):
    def __init__(self, reply_q, conn, allowed_remote_exmods):
        self.conn = conn
        self.allowed_remote_exmods = allowed_remote_exmods
        self.msg_id_cache = rpc_common._MsgIdCache()
        self.waiters = ReplyWaiters(reply_q)
        self.conn.declare_direct_consumer(reply_q, self)
        self.reply_q = reply_q
        # self._thread_exit_event = threading.Event()
        self._thread_exit_event = False
        # self._thread = threading.Thread(target=self.poll)
        self._thread = eventlet.spawn_n(self.poll)
        # self._thread.daemon = True
        # self._thread.start()

    def stop(self):
        if self._thread:
            # self._thread_exit_event.set()
            self._thread_exit_event = True
            self.conn.stop_consuming()
            # self._thread.join()
            self._thread = None

    def poll(self):
        # while not self._thread_exit_event.is_set():
        while not self._thread_exit_event:
            try:
                self.conn.consume()
            except Exception:
                LOG.exception("Failed to process incoming message, retrying...")

    def __call__(self, message):
        # This message is simpleservice.rpc.driver.message.RabbitMessage
        message.acknowledge()
        incoming_msg_id = message.pop('_msg_id', None)
        if message.get('ending'):
            LOG.debug("received reply msg_id: %s", incoming_msg_id)
        self.waiters.put(incoming_msg_id, message)

    def listen(self, msg_id):
        self.waiters.add(msg_id)

    def unlisten(self, msg_id):
        self.waiters.remove(msg_id)

    @staticmethod
    def _raise_timeout_exception(msg_id, reply_q):
        if rpc_common.MsgTimeoutRecorder is not None:
            rpc_common.MsgTimeoutRecorder(msg_id, reply_q, 'Timeout')
        raise exceptions.MessagingTimeout('Timed out waiting for a reply to message ID %s.' % msg_id)

    def _process_reply(self, data):
        self.msg_id_cache.check_duplicate_message(data)
        if data['failure']:
            failure = data['failure']
            result = rpc_common.deserialize_remote_exception(
                failure, self.allowed_remote_exmods)
        else:
            result = data.get('result', None)

        ending = data.get('ending', False)
        return result, ending

    def wait(self, msg_id, timeout):
        # NOTE(sileht): for each msg_id we receive two amqp message
        # first one with the payload, a second one to ensure the other
        # have finish to send the payload
        # NOTE(viktors): We are going to remove this behavior in the N
        # release, but we need to keep backward compatibility, so we should
        # support both cases for now.
        timer = rpc_common.DecayingTimer(duration=timeout)
        timer.start()
        final_reply = None
        ending = False
        while not ending:
            timeout = timer.check_return(self._raise_timeout_exception, msg_id, self.reply_q)
            try:
                message = self.waiters.get(msg_id, timeout=timeout)
            # except moves.queue.Empty:
            except eventlet.queue.Empty:
                self._raise_timeout_exception(msg_id, self.reply_q)
            reply, ending = self._process_reply(message)
            if reply is not None:
                # NOTE(viktors): This can be either first _send_reply() with an
                # empty `result` field or a second _send_reply() with
                # ending=True and no `result` field.
                final_reply = reply
        return final_reply


class RabbitDriver(object):

    prefetch_size = 0

    missing_destination_retry_timeout = 0

    def __init__(self, conf):

        self.missing_destination_retry_timeout = conf.kombu_missing_consumer_retry_timeout
        self.prefetch_size = conf.rabbit_qos_prefetch_count
        connection_pool = connection.ConnectionPool(conf)
        self.conf = conf
        self._allowed_remote_exmods = []
        self._default_exchange = conf.exchange
        # self._default_exchange = default_exchange
        self._connection_pool = connection_pool
        # self._reply_q_lock = threading.Lock()
        self._reply_q_lock = eventlet.semaphore.Semaphore()
        self._reply_q = None
        self._reply_q_conn = None
        self._waiter = None

    def init_timeout_record(self, session):
        """this init func for set MsgTimeoutRecorder
        so that, ReplyWaiter can wirite timeout log
        into database
        """
        if rpc_common.MsgTimeoutRecorder is not None:
            raise RuntimeError('Do not init MsgTimeoutRecorder more then once')

        def record_closure(msg_id, queue_name, raw_message):
            """A closure for write message into database"""
            row = MsgTimeoutRecord(record_time=Gkey(),
                                   msg_id=msg_id, queue_name=queue_name,
                                   raw_message=raw_message)
            session.add(row)
            session.flush()

        rpc_common.MsgTimeoutRecorder = record_closure

    def _get_exchange(self, target):
        return target.exchange or self._default_exchange

    def _get_connection(self, purpose=rpc_common.PURPOSE_SEND):
        return connection.ConnectionContext(self._connection_pool,
                                            purpose=purpose)

    def _init_waiter(self):
        if self._reply_q is None:
            with self._reply_q_lock:
                # double check with lock
                if self._reply_q is None:
                    reply_q = 'reply_' + uuid.uuid4().hex
                    conn = self._get_connection(rpc_common.PURPOSE_LISTEN)
                    self._waiter = ReplyWaiter(reply_q, conn,
                                               self._allowed_remote_exmods)
                    self._reply_q = reply_q
                    self._reply_q_conn = conn

    def _get_reply_q(self):
        if self._reply_q is None:
            self._init_waiter()
        return self._reply_q

    def _send(self, target, ctxt, message,
              wait_for_reply=None, timeout=None,
              notify=False, retry=None):
        context = ctxt
        msg = message
        # Set namespace for dispatcher
        ctxt.update({'namespace': target.namespace,
                     'casttime': int(realnow())})
        if wait_for_reply:
            # ctxt.update({'reply': True})
            msg_id = uuid.uuid4().hex
            msg.update({'_msg_id': msg_id})
            msg.update({'_reply_q': self._get_reply_q()})
        rpc_common._add_unique_id(msg)
        unique_id = msg[rpc_common.UNIQUE_ID]
        rpc_common.pack_context(msg, context)
        msg = rpc_common.serialize_msg(msg)
        if wait_for_reply:
            self._waiter.listen(msg_id)
            log_msg = "CALL msg_id: %s " % msg_id
        else:
            log_msg = "CAST unique_id: %s " % unique_id
        try:
            with self._get_connection(rpc_common.PURPOSE_SEND) as conn:
                if notify:
                    exchange = self._get_exchange(target)
                    log_msg += "NOTIFY exchange '%(exchange)s'" \
                               " topic '%(topic)s'" % {
                                   'exchange': exchange,
                                   'topic': target.topic}
                    LOG.debug(log_msg)
                    conn.notify_send(exchange, target.topic, msg, retry=retry)
                elif target.fanout:
                    log_msg += "FANOUT topic '%(topic)s'" % {
                        'topic': target.topic}
                    LOG.debug(log_msg)
                    conn.fanout_send(target.fanout, msg, retry=retry)
                else:
                    topic = target.topic
                    exchange = self._get_exchange(target)
                    if target.server:
                        topic = '%s.%s' % (target.topic, target.server)
                    log_msg += "exchange '%(exchange)s' topic '%(topic)s'" % \
                               {'exchange': exchange, 'topic': target.topic}
                    LOG.debug(log_msg)
                    conn.topic_send(exchange_name=exchange, topic=topic,
                                    msg=msg, timeout=timeout, retry=retry)

            if wait_for_reply:
                result = self._waiter.wait(msg_id, timeout)
                if isinstance(result, Exception):
                    raise result
                return result
        finally:
            if wait_for_reply:
                self._waiter.unlisten(msg_id)

    def send(self, target, ctxt, message, wait_for_reply=None, timeout=None,
             retry=None):
        return self._send(target, ctxt, message, wait_for_reply, timeout,
                          retry=retry)

    def send_notification(self, target, ctxt, message, retry=None):
        return self._send(target, ctxt, message,
                          # envelope=(version == 2.0), notify=True, retry=retry)
                          notify=True, retry=retry)

    def listen(self, targets):
        conn = self._get_connection(rpc_common.PURPOSE_LISTEN)
        listener = poller.AMQPListener(self, conn)
        for target in targets:
            if not target:
                continue
            if target.topic:
                conn.declare_topic_consumer(exchange_name=self._get_exchange(target),
                                            topic=target.topic,
                                            callback=listener)
                LOG.info('Listen on topic %s' % target.topic)
                conn.declare_topic_consumer(exchange_name=self._get_exchange(target),
                                            topic='%s.%s' % (target.topic,
                                                             target.server),
                                            callback=listener)
                LOG.info('Listen on topic %s.%s' % (target.topic, target.server))
            if target.fanout:
                conn.declare_fanout_consumer(target.fanout, listener)
                LOG.info('Listen on fanout %s' % target.fanout)
        # self._init_waiter()
        return listener

    def cleanup(self):
        if self._connection_pool:
            self._connection_pool.empty()
        self._connection_pool = None

        with self._reply_q_lock:
            if self._reply_q is not None:
                self._waiter.stop()
                self._reply_q_conn.close()
                self._reply_q_conn = None
                self._reply_q = None
                self._waiter = None

    def require_features(self, requeue=True):
        pass
