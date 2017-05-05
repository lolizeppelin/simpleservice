import time

from simpleutil.utils import timeutils

from simpleutil.log import log as logging

from simpleservice.rpc.driver import common as rpc_common
from simpleservice.rpc.driver import exceptions

LOG = logging.getLogger(__name__)


class RabbitMessage(dict):
    """Listener recv this type of message from __call__"""
    def __init__(self, raw_message):
        # raw_message is kombu.transport.pyamqp.Message
        super(RabbitMessage, self).__init__(
            rpc_common.deserialize_msg(raw_message.payload))
        LOG.trace('RabbitMessage.Init: message %s', self)
        self._raw_message = raw_message

    def acknowledge(self):
        LOG.trace('RabbitMessage.acknowledge: message %s', self)
        self._raw_message.ack()

    def requeue(self):
        LOG.trace('RabbitMessage.requeue: message %s', self)
        self._raw_message.requeue()


class AMQPIncomingMessage(object):

    def __init__(self, listener, ctxt, message, unique_id, msg_id, reply_q,
                 obsolete_reply_queues):
        """
        message is Intance of
        simpleservice.rpc.driver.message.RabbitMessage
        AMQPIncomingMessage for dispather
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