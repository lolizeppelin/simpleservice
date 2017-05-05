# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import sys
import os
import six
import uuid
import ssl
import collections
import contextlib
import itertools
import socket
import functools

import eventlet
import eventlet.hubs
import eventlet.semaphore

import kombu
import kombu.connection
import kombu.entity
import kombu.messaging

from simpleutil.utils.timeutils import monotonic
from simpleutil.utils.lockutils import DummyLock
from simpleutil.utils.lockutils import PriorityLock

from simpleutil.log import log as logging

from simpleservice.rpc.driver.message import RabbitMessage
from simpleservice.rpc.driver import common as rpc_common
from simpleservice.rpc.driver import exceptions

LOG = logging.getLogger(__name__)

TCP_USER_TIMEOUT = 18

hub = eventlet.hubs.get_hub()

def _get_queue_arguments(rabbit_ha_queues, rabbit_queue_ttl):
    args = {}
    if rabbit_ha_queues:
        args['x-ha-policy'] = 'all'
    if rabbit_queue_ttl > 0:
        args['x-expires'] = rabbit_queue_ttl * 1000
    return args


class Consumer(object):
    """Consumer class."""

    def __init__(self, exchange_name, queue_name, routing_key, type, durable,
                 exchange_auto_delete, queue_auto_delete, callback,
                 nowait=True, rabbit_ha_queues=None, rabbit_queue_ttl=0):
        """Init the Publisher class with the exchange_name, routing_key,
        type, durable auto_delete
        """
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.exchange_auto_delete = exchange_auto_delete
        self.queue_auto_delete = queue_auto_delete
        self.durable = durable
        self.callback = callback
        self.type = type
        self.nowait = nowait
        self.queue_arguments = _get_queue_arguments(rabbit_ha_queues,
                                                    rabbit_queue_ttl)

        self.queue = None
        self.exchange = kombu.entity.Exchange(
            name=exchange_name,
            type=type,
            durable=self.durable,
            auto_delete=self.exchange_auto_delete)

    def declare(self, conn):
        """Re-declare the queue after a rabbit (re)connect."""
        self.queue = kombu.entity.Queue(
            name=self.queue_name,
            channel=conn.channel,
            exchange=self.exchange,
            durable=self.durable,
            auto_delete=self.queue_auto_delete,
            routing_key=self.routing_key,
            queue_arguments=self.queue_arguments)

        try:
            LOG.trace('ConsumerBase.declare: '
                      'queue %s', self.queue_name)
            self.queue.declare()
        except conn.connection.channel_errors as exc:
            # NOTE(jrosenboom): This exception may be triggered by a race
            # condition. Simply retrying will solve the error most of the time
            # and should work well enough as a workaround until the race
            # condition itself can be fixed.
            # See https://bugs.launchpad.net/neutron/+bug/1318721 for details.
            if exc.code == 404:
                self.queue.declare()
            else:
                raise

    def consume(self, tag):
        """Actually declare the consumer on the amqp channel.  This will
        start the flow of messages from the queue.  Using the
        Connection.consume() will process the messages,
        calling the appropriate callback.
        """

        self.queue.consume(callback=self._callback,
                           consumer_tag=six.text_type(tag),
                           nowait=self.nowait)

    def cancel(self, tag):
        LOG.trace('ConsumerBase.cancel: canceling %s', tag)
        self.queue.cancel(six.text_type(tag))

    def _callback(self, message):
        """Call callback with deserialized message.
        Messages that are processed and ack'ed.
        """
        # message is amqp.basic_message.Message
        m2p = getattr(self.queue.channel, 'message_to_python', None)
        if m2p:
            message = m2p(message)
        try:
            # message is kombu.transport.pyamqp.Message after message_to_python
            self.callback(RabbitMessage(message))
        except Exception:
            LOG.exception("Failed to process message"
                          " ... skipping it.")
            message.ack()


class Connection(object):
    """Connection object."""
    pools = {}
    _SSL_PROTOCOLS = {
        "tlsv1": ssl.PROTOCOL_TLSv1,
        "sslv23": ssl.PROTOCOL_SSLv23
    }
    _OPTIONAL_PROTOCOLS = {
        'sslv2': 'PROTOCOL_SSLv2',
        'sslv3': 'PROTOCOL_SSLv3',
        'tlsv1_1': 'PROTOCOL_TLSv1_1',
        'tlsv1_2': 'PROTOCOL_TLSv1_2',
    }
    for protocol in _OPTIONAL_PROTOCOLS:
        try:
            _SSL_PROTOCOLS[protocol] = getattr(ssl,
                                               _OPTIONAL_PROTOCOLS[protocol])
        except AttributeError:
            pass

    def __init__(self, conf, purpose):
        # NOTE(viktors): Parse config options
        driver_conf = conf.rabbit

        self.max_retries = driver_conf.rabbit_max_retries
        self.interval_start = driver_conf.rabbit_retry_interval
        self.interval_stepping = driver_conf.rabbit_retry_backoff
        self.interval_max = driver_conf.rabbit_interval_max
        self.login_method = driver_conf.rabbit_login_method
        # self.fake_rabbit = driver_conf.fake_rabbit
        self.virtual_host = driver_conf.rabbit_virtual_host
        self.rabbit_host = driver_conf.rabbit_host
        # self.rabbit_hosts = driver_conf.rabbit_hosts
        self.rabbit_port = driver_conf.rabbit_port
        self.rabbit_userid = driver_conf.rabbit_userid
        self.rabbit_password = driver_conf.rabbit_password
        self.rabbit_ha_queues = driver_conf.rabbit_ha_queues
        self.rabbit_transient_queues_ttl = driver_conf.rabbit_transient_queues_ttl
        self.rabbit_qos_prefetch_count = driver_conf.rabbit_qos_prefetch_count
        self.heartbeat_timeout_threshold = driver_conf.heartbeat_timeout_threshold
        self.heartbeat_rate = driver_conf.heartbeat_rate
        self.kombu_reconnect_delay = driver_conf.kombu_reconnect_delay
        self.amqp_durable_queues = driver_conf.amqp_durable_queues
        self.amqp_auto_delete = driver_conf.amqp_auto_delete
        self.rabbit_use_ssl = driver_conf.rabbit_use_ssl
        self.kombu_missing_consumer_retry_timeout = \
            driver_conf.kombu_missing_consumer_retry_timeout
        self.kombu_failover_strategy = driver_conf.kombu_failover_strategy
        self.kombu_compression = driver_conf.kombu_compression

        if self.rabbit_use_ssl:
            self.kombu_ssl_version = driver_conf.kombu_ssl_version
            self.kombu_ssl_keyfile = driver_conf.kombu_ssl_keyfile
            self.kombu_ssl_certfile = driver_conf.kombu_ssl_certfile
            self.kombu_ssl_ca_certs = driver_conf.kombu_ssl_ca_certs

        # Try forever?
        if self.max_retries <= 0:
            self.max_retries = None

        self._url = "amqp://%(username)s:%(password)s" \
                    "@%(host)s:%(port)s/%(vhost)s" % \
                    {'username': self.rabbit_userid, 'password':self.rabbit_password,
                     'host':self.rabbit_host, 'port':self.rabbit_port,
                     'vhost':self.virtual_host}

        self._initial_pid = os.getpid()
        self._consumers = {}
        self._new_tags = set()
        self._active_tags = {}
        self._tags = itertools.count(1)

        self._consume_loop_stopped = False
        self.channel = None
        self.purpose = purpose

        self.last_time = monotonic()
        if purpose == rpc_common.PURPOSE_SEND:
            self._connection_lock = PriorityLock()
            self._connection_lock.set_defalut_priority(1)
        else:
            self._connection_lock = DummyLock()

        self.connection = kombu.connection.Connection(
            self._url, ssl=self._fetch_ssl_params(),
            login_method=self.login_method,
            heartbeat=self.heartbeat_timeout_threshold,
            failover_strategy=self.kombu_failover_strategy,
            transport_options={
                'confirm_publish': True,
                'client_properties': {'capabilities': {
                    'authentication_failure_close': True,
                    'connection.blocked': True,
                    'consumer_cancel_notify': True}},
                'on_blocked': self._on_connection_blocked,
                'on_unblocked': self._on_connection_unblocked,
            },
        )

        LOG.debug('Connecting to AMQP server on %(hostname)s:%(port)s',
                  self.connection.info())

        self._heartbeat_wait_timeout = (
            float(self.heartbeat_timeout_threshold) /
            float(self.heartbeat_rate) / 2.0)
        self._heartbeat_support_log_emitted = False

        # NOTE(sileht): just ensure the connection is setuped at startup
        self.ensure_connection()

        # NOTE(sileht): if purpose is PURPOSE_LISTEN
        # the consume code does the heartbeat stuff
        # we don't need a thread
        self._heartbeat_thread = None
        if purpose == rpc_common.PURPOSE_SEND:
            self._heartbeat_start()

        LOG.debug('Connected to AMQP server on %(hostname)s:%(port)s '
                  'via [%(transport)s] client',
                  self.connection.info())
        # NOTE(sileht): value chosen according the best practice from kombu
        # http://kombu.readthedocs.org/en/latest/reference/kombu.common.html#kombu.common.eventloop
        # For heatbeat, we can set a bigger timeout, and check we receive the
        # heartbeat packets regulary
        if self._heartbeat_supported_and_enabled():
            self._poll_timeout = self._heartbeat_wait_timeout
        else:
            self._poll_timeout = 1

    @classmethod
    def validate_ssl_version(cls, version):
        key = version.lower()
        try:
            return cls._SSL_PROTOCOLS[key]
        except KeyError:
            raise RuntimeError("Invalid SSL version : %s" % version)

    def _parse_url_hostname(self, hostname):
        """Handles hostname returned from urlparse and checks whether it's
        ipaddress. If it's ipaddress it ensures that it has brackets for IPv6.
        """
        return '[%s]' % hostname if ':' in hostname else hostname

    def _fetch_ssl_params(self):
        """Handles fetching what ssl params should be used for the connection
        (if any).
        """
        if self.rabbit_use_ssl:
            ssl_params = dict()

            # http://docs.python.org/library/ssl.html - ssl.wrap_socket
            if self.kombu_ssl_version:
                ssl_params['ssl_version'] = self.validate_ssl_version(
                    self.kombu_ssl_version)
            if self.kombu_ssl_keyfile:
                ssl_params['keyfile'] = self.kombu_ssl_keyfile
            if self.kombu_ssl_certfile:
                ssl_params['certfile'] = self.kombu_ssl_certfile
            if self.kombu_ssl_ca_certs:
                ssl_params['ca_certs'] = self.kombu_ssl_ca_certs
                # We might want to allow variations in the
                # future with this?
                ssl_params['cert_reqs'] = ssl.CERT_REQUIRED
            return ssl_params or True
        return False

    @staticmethod
    def _on_connection_blocked(reason):
        LOG.error("The broker has blocked the connection: %s" % reason)

    @staticmethod
    def _on_connection_unblocked():
        LOG.info("The broker has unblocked the connection")

    def ensure_connection(self):
        # NOTE(sileht): we reset the channel and ensure
        # the kombu underlying connection works
        self._set_current_channel(None)
        self.ensure(method=lambda: self.connection.connection)
        self.set_transport_socket_timeout()

    def ensure(self, method, retry=None,
               recoverable_error_callback=None, error_callback=None,
               timeout_is_error=True):
        """Will retry up to retry number of times.
        retry = None means use the value of rabbit_max_retries
        retry = -1 means to retry forever
        retry = 0 means no retry
        retry = N means N retries

        NOTE(sileht): Must be called within the connection lock
        """
        current_pid = os.getpid()
        if self._initial_pid != current_pid:
            LOG.warning("Process forked after connection established! "
                        "This can result in unpredictable behavior. "
                        "See: http://docs.openstack.org/developer/"
                        "oslo.messaging/transport.html")
            self._initial_pid = current_pid

        if retry is None:
            retry = self.max_retries
        if retry is None or retry < 0:
            retry = None

        def on_error(exc, interval):
            LOG.debug("Received recoverable error from kombu:",
                      exc_info=True)

            recoverable_error_callback and recoverable_error_callback(exc)

            interval = (self.kombu_reconnect_delay + interval
                        if self.kombu_reconnect_delay > 0
                        else interval)

            info = {'err_str': exc, 'sleep_time': interval}
            info.update(self.connection.info())

            if 'Socket closed' in six.text_type(exc):
                LOG.error('AMQP server %(hostname)s:%(port)s closed'
                          'the connection. Check login credentials:%(err_str)s' % info)
            else:
                LOG.error('AMQP server on %(hostname)s:%(port)s is '
                          'unreachable: %(err_str)s. Trying again in '
                          '%(sleep_time)d seconds.' % info)

            if self.kombu_reconnect_delay > 0:
                LOG.trace('Delaying reconnect for %1.1f seconds ...',
                          self.kombu_reconnect_delay)
                # time.sleep(self.kombu_reconnect_delay)
                eventlet.sleep(self.kombu_reconnect_delay)

        def on_reconnection(new_channel):
            """Callback invoked when the kombu reconnects and creates
            a new channel, we use it the reconfigure our consumers.
            """

            self.set_transport_socket_timeout()
            self._set_current_channel(new_channel)
            for consumer in self._consumers:
                consumer.declare(self)

            LOG.info('Reconnected to AMQP server on '
                     '%(hostname)s:%(port)s via [%(transport)s] client' % self.connection.info())

        def execute_method(channel):
            self._set_current_channel(channel)
            method()

        # NOTE(sileht): Some dummy driver like the in-memory one doesn't
        # have notion of recoverable connection, so we must raise the original
        # exception like kombu does in this case.
        has_modern_errors = hasattr(
            self.connection.transport, 'recoverable_connection_errors',
        )
        if has_modern_errors:
            recoverable_errors = (
                self.connection.recoverable_channel_errors +
                self.connection.recoverable_connection_errors)
        else:
            recoverable_errors = ()

        try:
            autoretry_method = self.connection.autoretry(
                execute_method, channel=self.channel,
                max_retries=retry,
                errback=on_error,
                interval_start=self.interval_start or 1,
                interval_step=self.interval_stepping,
                interval_max=self.interval_max,
                on_revive=on_reconnection)
            ret, channel = autoretry_method()
            self._set_current_channel(channel)
            return ret
        except recoverable_errors as exc:
            LOG.debug("Received recoverable error from kombu:",
                      exc_info=True)
            error_callback and error_callback(exc)
            self._set_current_channel(None)
            # NOTE(sileht): number of retry exceeded and the connection
            # is still broken
            info = {'err_str': exc, 'retry': retry}
            info.update(self.connection.info())
            msg = 'Unable to connect to AMQP server on ' \
                  '%(hostname)s:%(port)s after ' \
                  '%(retry)s tries: %(err_str)s' % info
            LOG.error(msg)
            raise exceptions.MessageDeliveryFailure(msg)
        except exceptions.AMQPDestinationNotFound:
            # NOTE(sileht): we must reraise this without
            # trigger error_callback
            raise
        except Exception as exc:
            error_callback and error_callback(exc)
            raise

    def _set_current_channel(self, new_channel):
        """Change the channel to use.

        NOTE(sileht): Must be called within the connection lock
        """
        if new_channel == self.channel:
            return

        if self.channel is not None:
            self.PUBLISHER_DECLARED_QUEUES.pop(self.channel, None)
            self.connection.maybe_close_channel(self.channel)

        self.channel = new_channel

        if (new_channel is not None and
           self.purpose == rpc_common.PURPOSE_LISTEN):
            self._set_qos(new_channel)

    def _set_qos(self, channel):
        """Set QoS prefetch count on the channel"""
        if self.rabbit_qos_prefetch_count > 0:
            channel.basic_qos(0,
                              self.rabbit_qos_prefetch_count,
                              False)

    def close(self):
        """Close/release this connection."""
        self._heartbeat_stop()
        if self.connection:
            self._set_current_channel(None)
            self.connection.release()
            self.connection = None

    def reset(self):
        """Reset a connection so it can be used again."""
        recoverable_errors = (self.connection.recoverable_channel_errors +
                              self.connection.recoverable_connection_errors)

        with self._connection_lock:
            try:
                for consumer, tag in self._consumers.items():
                    consumer.cancel(tag=tag)
            except recoverable_errors:
                self.ensure_connection()
            self._consumers.clear()
            self._active_tags.clear()
            self._new_tags.clear()
            self._tags = itertools.count(1)

    def _heartbeat_supported_and_enabled(self):
        if self.heartbeat_timeout_threshold <= 0:
            return False

        if self.connection.supports_heartbeats:
            return True
        elif not self._heartbeat_support_log_emitted:
            LOG.warning("Heartbeat support requested but it is not "
                        "supported by the kombu driver or the broker")
            self._heartbeat_support_log_emitted = True
        return False

    def set_transport_socket_timeout(self, timeout=None):
        # NOTE(sileht): they are some case where the heartbeat check
        # or the producer.send return only when the system socket
        # timeout if reach. kombu doesn't allow use to customise this
        # timeout so for py-amqp we tweak ourself
        # NOTE(dmitryme): Current approach works with amqp==1.4.9 and
        # kombu==3.0.33. Once the commit below is released, we should
        # try to set the socket timeout in the constructor:
        # https://github.com/celery/py-amqp/pull/64

        heartbeat_timeout = self.heartbeat_timeout_threshold
        if self._heartbeat_supported_and_enabled():
            # NOTE(sileht): we are supposed to send heartbeat every
            # heartbeat_timeout, no need to wait more otherwise will
            # disconnect us, so raise timeout earlier ourself
            if timeout is None:
                timeout = heartbeat_timeout
            else:
                timeout = min(heartbeat_timeout, timeout)

        try:
            sock = self.channel.connection.sock
        except AttributeError as e:
            # Level is set to debug because otherwise we would spam the logs
            LOG.debug('Failed to get socket attribute: %s' % str(e))
        else:
            sock.settimeout(timeout)
            if sys.platform != 'win32':
                sock.setsockopt(socket.IPPROTO_TCP,
                                TCP_USER_TIMEOUT,
                                timeout * 1000 if timeout is not None else 0)

    @contextlib.contextmanager
    def _transport_socket_timeout(self, timeout):
        self.set_transport_socket_timeout(timeout)
        yield
        self.set_transport_socket_timeout()

    def _heartbeat_check(self):
        # NOTE(sileht): we are supposed to send at least one heartbeat
        # every heartbeat_timeout_threshold, so no need to way more
        self.connection.heartbeat_check(rate=self.heartbeat_rate)

    def _heartbeat_start(self):
        if self._heartbeat_supported_and_enabled():
            self._heartbeat_exit_event = False
            self._heartbeat_thread = eventlet.spawn_n(self._heartbeat_thread_job)[1]
            # To sure _heartbeat_thread start first and
            # Be the first one get _connection_lock
            # See doc of PriorityLock
            eventlet.sleep(0)
        else:
            self._heartbeat_thread = None

    def _heartbeat_stop(self):
        if self._heartbeat_thread is not None:
            # self._heartbeat_exit_event.set()
            self._heartbeat_exit_event = True
            eventlet.sleep(0.05)
            # self._heartbeat_thread.join()
            self._heartbeat_thread = None

    def _heartbeat_thread_job(self):
        """Thread that maintains inactive connections
        """
        # while not self._heartbeat_exit_event.is_set():
        while not self._heartbeat_exit_event:
            start = monotonic()
            with self._connection_lock.priority(0):
                if self._heartbeat_exit_event:
                    break
                recoverable_errors = (
                    self.connection.recoverable_channel_errors +
                    self.connection.recoverable_connection_errors)
                try:
                    try:
                        self._heartbeat_check()
                        try:
                            self.connection.drain_events(timeout=0.001)
                        except socket.timeout:
                            pass
                    except recoverable_errors as exc:
                        LOG.info("A recoverable connection/channel error occurred, "
                                 "trying to reconnect: %s" % exc)
                        self.ensure_connection()
                except Exception:
                    LOG.warning("Unexpected error during heartbeart "
                                "thread processing, retrying...")
                    LOG.debug('Exception', exc_info=True)
                if self._heartbeat_exit_event:
                    break
            sleep_time = self._heartbeat_wait_timeout + start - monotonic()
            if sleep_time >= 0.0:
                eventlet.sleep(sleep_time)

    def declare_consumer(self, consumer):
        """Create a Consumer using the class that was passed in and
        add it to our list of consumers
        """
        def _connect_error(exc):
            log_info = {'topic': consumer.routing_key, 'err_str': exc}
            LOG.error("Failed to declare consumer for topic '%(topic)s': "
                      "%(err_str)s" % log_info)

        def _declare_consumer():
            consumer.declare(self)
            tag = self._active_tags.get(consumer.queue_name)
            if tag is None:
                tag = next(self._tags)
                self._active_tags[consumer.queue_name] = tag
                self._new_tags.add(tag)

            self._consumers[consumer] = tag
            return consumer

        with self._connection_lock:
            return self.ensure(_declare_consumer,
                               error_callback=_connect_error)

    def consume(self, timeout=None):
        """Consume from all queues/consumers."""

        timer = rpc_common.DecayingTimer(duration=timeout)
        timer.start()

        def _raise_timeout(exc):
            LOG.debug('Timed out waiting for RPC response: %s', exc)
            raise exceptions.Timeout()

        def _recoverable_error_callback(exc):
            if not isinstance(exc, exceptions.Timeout):
                self._new_tags = set(self._consumers.values())
            timer.check_return(_raise_timeout, exc)

        def _error_callback(exc):
            _recoverable_error_callback(exc)
            LOG.error('Failed to consume message from queue: %s' % exc)

        def _consume():
            # NOTE(sileht): in case the acknowledgment or requeue of a
            # message fail, the kombu transport can be disconnected
            # In this case, we must redeclare our consumers, so raise
            # a recoverable error to trigger the reconnection code.
            if not self.connection.connected:
                raise self.connection.recoverable_connection_errors[0]

            if self._new_tags:
                for consumer, tag in self._consumers.items():
                    if tag in self._new_tags:
                        consumer.consume(tag=tag)
                        self._new_tags.remove(tag)

            poll_timeout = (self._poll_timeout if timeout is None
                            else min(timeout, self._poll_timeout))
            while True:
                if self._consume_loop_stopped:
                    return

                if self._heartbeat_supported_and_enabled():
                    self._heartbeat_check()

                try:
                    self.connection.drain_events(timeout=poll_timeout)
                    return
                except socket.timeout as exc:
                    poll_timeout = timer.check_return(
                        _raise_timeout, exc, maximum=self._poll_timeout)

        with self._connection_lock:
            self.ensure(_consume,
                        recoverable_error_callback=_recoverable_error_callback,
                        error_callback=_error_callback)

    def stop_consuming(self):
        self._consume_loop_stopped = True

    def declare_direct_consumer(self, topic, callback):
        """Create a 'direct' queue.
        In nova's use, this is generally a msg_id queue used for
        responses for call/multicall
        """

        consumer = Consumer(exchange_name=topic,
                            queue_name=topic,
                            routing_key=topic,
                            type='direct',
                            durable=False,
                            exchange_auto_delete=True,
                            queue_auto_delete=False,
                            callback=callback,
                            rabbit_ha_queues=self.rabbit_ha_queues,
                            rabbit_queue_ttl=self.rabbit_transient_queues_ttl)

        self.declare_consumer(consumer)

    def declare_topic_consumer(self, exchange_name, topic, callback=None,
                               queue_name=None):
        """Create a 'topic' consumer."""
        consumer = Consumer(exchange_name=exchange_name,
                            queue_name=queue_name or topic,
                            routing_key=topic,
                            type='topic',
                            durable=self.amqp_durable_queues,
                            exchange_auto_delete=self.amqp_auto_delete,
                            queue_auto_delete=self.amqp_auto_delete,
                            callback=callback,
                            rabbit_ha_queues=self.rabbit_ha_queues)

        self.declare_consumer(consumer)

    def declare_fanout_consumer(self, topic, callback):
        """Create a 'fanout' consumer."""

        unique = uuid.uuid4().hex
        exchange_name = '%s_fanout' % topic
        queue_name = '%s_fanout_%s' % (topic, unique)

        consumer = Consumer(exchange_name=exchange_name,
                            queue_name=queue_name,
                            routing_key=topic,
                            type='fanout',
                            durable=False,
                            exchange_auto_delete=True,
                            queue_auto_delete=False,
                            callback=callback,
                            rabbit_ha_queues=self.rabbit_ha_queues,
                            rabbit_queue_ttl=self.rabbit_transient_queues_ttl)

        self.declare_consumer(consumer)

    def _ensure_publishing(self, method, exchange, msg, routing_key=None,
                           timeout=None, retry=None):
        """Send to a publisher based on the publisher class."""

        def _error_callback(exc):
            log_info = {'topic': exchange.name, 'err_str': exc}
            LOG.error("Failed to publish message to topic "
                      "'%(topic)s': %(err_str)s" % log_info)
            LOG.debug('Exception', exc_info=exc)

        method = functools.partial(method, exchange, msg, routing_key, timeout)

        with self._connection_lock:
            self.ensure(method, retry=retry, error_callback=_error_callback)
        # while self._connection_lock:
        #     eventlet.sleep(0)
        # self._connection_lock = True
        # self.ensure(method, retry=retry, error_callback=_error_callback)
        # self._connection_lock = False

    def _publish(self, exchange, msg, routing_key=None, timeout=None):
        """Publish a message."""
        producer = kombu.messaging.Producer(exchange=exchange,
                                            channel=self.channel,
                                            auto_declare=not exchange.passive,
                                            routing_key=routing_key)

        log_info = {'msg': msg,
                    'who': exchange or 'default',
                    'key': routing_key}
        LOG.trace('Connection._publish: sending message %(msg)s to'
                  ' %(who)s with routing key %(key)s', log_info)

        # NOTE(sileht): no need to wait more, caller expects
        # a answer before timeout is reached
        with self._transport_socket_timeout(timeout):
            # NOTE(gcb) kombu accept TTL as seconds instead of millisecond since
            # version 3.0.25, so do conversion according to kombu version.
            # with requirement kombu >=3.0.25
            # producer.publish(msg, expiration=self._get_expiration(timeout),
            producer.publish(msg, expiration=int(timeout * 1000),
                             # Json only
                             content_type='application/json',
                             content_encoding = 'utf-8',
                             compression=self.kombu_compression)

    # List of notification queue declared on the channel to avoid
    # unnecessary redeclaration. This list is resetted each time
    # the connection is resetted in Connection._set_current_channel
    PUBLISHER_DECLARED_QUEUES = collections.defaultdict(set)

    def _publish_and_creates_default_queue(self, exchange, msg,
                                           routing_key=None, timeout=None):
        """Publisher that declares a default queue

        When the exchange is missing instead of silently creates an exchange
        not binded to a queue, this publisher creates a default queue
        named with the routing_key

        This is mainly used to not miss notification in case of nobody consumes
        them yet. If the future consumer bind the default queue it can retrieve
        missing messages.

        _set_current_channel is responsible to cleanup the cache.
        """
        queue_indentifier = (exchange.name, routing_key)
        # NOTE(sileht): We only do it once per reconnection
        # the Connection._set_current_channel() is responsible to clear
        # this cache
        if (queue_indentifier not in
                self.PUBLISHER_DECLARED_QUEUES[self.channel]):
            queue = kombu.entity.Queue(
                channel=self.channel,
                exchange=exchange,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
                name=routing_key,
                routing_key=routing_key,
                queue_arguments=_get_queue_arguments(self.rabbit_ha_queues, 0))
            log_info = {'key': routing_key, 'exchange': exchange}
            LOG.trace(
                'Connection._publish_and_creates_default_queue: '
                'declare queue %(key)s on %(exchange)s exchange', log_info)
            queue.declare()
            self.PUBLISHER_DECLARED_QUEUES[self.channel].add(queue_indentifier)

        self._publish(exchange, msg, routing_key=routing_key, timeout=timeout)

    def _publish_and_raises_on_missing_exchange(self, exchange, msg,
                                                routing_key=None,
                                                timeout=None):
        """Publisher that raises exception if exchange is missing."""
        if not exchange.passive:
            raise RuntimeError("_publish_and_retry_on_missing_exchange() must "
                               "be called with an passive exchange.")

        try:
            self._publish(exchange, msg, routing_key=routing_key,
                          timeout=timeout)
            return
        except self.connection.channel_errors as exc:
            if exc.code == 404:
                # NOTE(noelbk/sileht):
                # If rabbit dies, the consumer can be disconnected before the
                # publisher sends, and if the consumer hasn't declared the
                # queue, the publisher's will send a message to an exchange
                # that's not bound to a queue, and the message wll be lost.
                # So we set passive=True to the publisher exchange and catch
                # the 404 kombu ChannelError and retry until the exchange
                # appears
                raise exceptions.AMQPDestinationNotFound(
                    "exchange %s doesn't exists" % exchange.name)
            raise

    def direct_send(self, msg_id, msg):
        """Send a 'direct' message."""
        exchange = kombu.entity.Exchange(name=msg_id,
                                         type='direct',
                                         durable=False,
                                         auto_delete=True,
                                         passive=True)

        self._ensure_publishing(self._publish_and_raises_on_missing_exchange,
                                exchange, msg, routing_key=msg_id)

    def topic_send(self, exchange_name, topic, msg, timeout=None, retry=None):
        """Send a 'topic' message."""
        exchange = kombu.entity.Exchange(
            name=exchange_name,
            type='topic',
            durable=self.amqp_durable_queues,
            auto_delete=self.amqp_auto_delete)

        self._ensure_publishing(self._publish, exchange, msg,
                                routing_key=topic, timeout=timeout,
                                retry=retry)

    def fanout_send(self, topic, msg, retry=None):
        """Send a 'fanout' message."""
        exchange = kombu.entity.Exchange(name='%s_fanout' % topic,
                                         type='fanout',
                                         durable=False,
                                         auto_delete=True)

        self._ensure_publishing(self._publish, exchange, msg, retry=retry)

    def notify_send(self, exchange_name, topic, msg, retry=None, **kwargs):
        """Send a notify message on a topic."""
        exchange = kombu.entity.Exchange(
            name=exchange_name,
            type='topic',
            durable=self.amqp_durable_queues,
            auto_delete=self.amqp_auto_delete)

        self._ensure_publishing(self._publish_and_creates_default_queue,
                                exchange, msg, routing_key=topic, retry=retry)


class ConnectionPool(object):
    """Class that implements a Pool of Connections."""
    def __init__(self, conf, rpc_conn_pool_size):
        self.conf = conf
        # self.url = url
        self._max_size = rpc_conn_pool_size
        self._current_size = 0
        # self._cond = threading.Condition()
        self._cond = eventlet.semaphore.Semaphore()
        self._items = collections.deque()
        self.reply_proxy = None

    def create(self, purpose=None):
        if purpose is None:
            # purpose = common.PURPOSE_SEND
            purpose = rpc_common.PURPOSE_SEND
        LOG.debug('Pool creating new connection')
        # return self.connection_cls(self.conf, self.url, purpose)
        return Connection(self.conf, purpose)

    def empty(self):
        for item in self.iter_free():
            item.close()

    def iter_free(self):
        """Iterate over free items."""
        with self._cond:
            while True:
                try:
                    yield self._items.popleft()
                except IndexError:
                    break

    def put(self, item):
        """Return an item to the pool."""
        with self._cond:
            self._items.appendleft(item)
        #     self._cond.notify()

    def get(self):
        """Return an item from the pool, when one is available.

        This may cause the calling thread to block.
        """
        with self._cond:
            while True:
                try:
                    return self._items.popleft()
                except IndexError:
                    pass
                if self._current_size < self._max_size:
                    self._current_size += 1
                    break
                eventlet.sleep(0)
        # We've grabbed a slot and dropped the lock, now do the creation
        try:
            return self.create()
        except Exception:
            with self._cond:
                self._current_size -= 1
                raise


class ConnectionContext(object):
    """The class that is actually returned to the create_connection() caller.

    This is essentially a wrapper around Connection that supports 'with'.
    It can also return a new Connection, or one from a pool.

    The function will also catch when an instance of this class is to be
    deleted.  With that we can return Connections to the pool on exceptions
    and so forth without making the caller be responsible for catching them.
    If possible the function makes sure to return a connection to the pool.
    """

    def __init__(self, connection_pool, purpose):
        """Create a new connection, or get one from the pool."""
        self.connection = None
        self.connection_pool = connection_pool
        pooled = purpose == rpc_common.PURPOSE_SEND
        if pooled:
            self.connection = connection_pool.get()
        else:
            # a non-pooled connection is requested, so create a new connection
            self.connection = connection_pool.create(purpose)
        self.pooled = pooled
        self.connection.pooled = pooled

    def __enter__(self):
        """When with ConnectionContext() is used, return self."""
        return self

    def _done(self):
        """If the connection came from a pool, clean it up and put it back.
        If it did not come from a pool, close it.
        """
        if self.connection:
            if self.pooled:
                # Reset the connection so it's ready for the next caller
                # to grab from the pool
                try:
                    self.connection.reset()
                except Exception:
                    LOG.exception("Fail to reset the connection, drop it")
                    try:
                        self.connection.close()
                    except Exception:
                        pass
                    self.connection = self.connection_pool.create()
                finally:
                    self.connection_pool.put(self.connection)
            else:
                try:
                    self.connection.close()
                except Exception:
                    pass
            self.connection = None

    def __exit__(self, exc_type, exc_value, tb):
        """End of 'with' statement.  We're done here."""
        self._done()

    def __del__(self):
        """Caller is done with this connection.  Make sure we cleaned up."""
        self._done()

    def close(self):
        """Caller is done with this connection."""
        self._done()

    def __getattr__(self, key):
        """Proxy all other calls to the Connection instance."""
        if self.connection:
            return getattr(self.connection, key)
        else:
            raise exceptions.InvalidRPCConnectionReuse()
