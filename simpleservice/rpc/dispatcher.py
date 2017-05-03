import sys

from simpleservice.rpc.driver import exceptions
from simpleservice.rpc.target import target_match

from simpleutil.log import log as logging

__all__ = [
    'RPCDispatcher',
    'DispatcherExecutorContext',
]

LOG = logging.getLogger(__name__)


class RPCDispatcher(object):

    def __init__(self, manager, endpoints):
        self.manager = manager
        self.endpoints = endpoints

    def _do_dispatch(self, endpoint, method, ctxt, args):
        """return dict
        """
        if endpoint:
            return self.manager.call_endpoint(endpoint, method, ctxt, args)
        else:
            func = getattr(self.manager, method)
            return func(ctxt, args)

    def __call__(self, incoming):
        if self.manager.full():
            incoming.requeue()
            LOG.info('RPCDispatcher find manager is full, requeue')
            return None
        incoming.acknowledge()
        return DispatcherExecutorContext(incoming=incoming, dispatch=self._dispatch)

    def _dispatch(self, incoming):
        """incoming type:AMQPIncomingMessage
        """
        ctxt = incoming.ctxt
        message = incoming.message
        method = message.get('method', None)
        args = message.get('args', {})
        # namespace = message.get('namespace')
        target = message.get('target', None)
        try:
            if target_match(target, self.manager.target):
                if not method.startswith('rpc_'):
                    method = 'rpc_%(method)s' % {'method': method}
                if hasattr(self.manager, method):
                    incoming.reply(self._do_dispatch(None, method, ctxt, args))
                    return
            for endpoint in self.endpoints:
                if not target_match(target, endpoint.target):
                    continue
                if hasattr(endpoint, method):
                    incoming.reply(self._do_dispatch(endpoint, method, ctxt, args))
                    return
                else:
                    raise exceptions.NoSuchMethod(method)
            raise exceptions.UnsupportedNamespace(target.namespace, method=method)
        except exceptions.ExpectedException as e:
            LOG.debug('Expected exception during message handling (%s)' % str(e.exc_info[1]))
            incoming.reply(failure=e.exc_info, log_failure=False)
        except Exception as e:
            exc_info = sys.exc_info()
            try:
                LOG.error('Exception during message handling: %s' % e)
                incoming.reply(failure=exc_info)
            finally:
                # NOTE(dhellmann): Remove circular object reference
                # between the current stack frame and the traceback in
                # exc_info.
                del exc_info


class DispatcherExecutorContext(object):
    def __init__(self, incoming, dispatch):
        self._incoming = incoming
        self._dispatch = dispatch

    def run(self):
        try:
            self._dispatch(self._incoming)
        except Exception:
            msg = 'The dispatcher method must catches all exceptions'
            LOG.exception(msg)
            raise RuntimeError(msg)

    def done(self, *args, **kwargs):
        pass
