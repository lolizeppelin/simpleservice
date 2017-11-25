import sys
import eventlet

from simpleservice.rpc.driver import exceptions
from simpleutil.log import log as logging


__all__ = [
    'RPCDispatcher',
    'DispatcherExecutorContext',
]

LOG = logging.getLogger(__name__)


class RPCDispatcher(object):

    def __init__(self, manager):
        self.manager = manager

    def _do_dispatch(self, endpoint, method, ctxt, args):
        """NOTE: Return dict just fine
        The Max deep is jsonutils.MAX_DEEP - 1
        """
        if endpoint:
            ret = self.manager.call_endpoint(endpoint, method, ctxt, **args)
        else:
            func = getattr(self.manager, method)
            ret = func(ctxt, **args)
        return ret

    def __call__(self, incoming):
        if self.manager.full():
            eventlet.sleep(0.01)
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
        try:
            method = message.pop('method')
        except KeyError:
            raise exceptions.NoSuchMethod('Method is None')
        if not method.startswith('rpc_'):
            method = 'rpc_%(method)s' % {'method': method}
        args = message.pop('args', {})
        namespace = ctxt.pop('namespace', None)
        try:
            if namespace == self.manager.namespace:
                if hasattr(self.manager, method):
                    incoming.reply(self._do_dispatch(None, method, ctxt, args))
                    return
                else:
                    raise exceptions.ManagerNoSuchMethod(method)
            for endpoint in self.manager.endpoints:
                if namespace != endpoint.namespace:
                    continue
                if hasattr(endpoint, method):
                    incoming.reply(self._do_dispatch(endpoint, method, ctxt, args))
                    return
                else:
                    raise exceptions.EndpointNoSuchMethod(endpoint.namespace, method)
            # msg_id is not None means get a rpc call
            # if a rpc call can not found endpoint
            # raise the UnsupportedNamespace error
            # rpc cast or notify will igonre this msg
            if incoming.msg_id:
                raise exceptions.UnsupportedNamespace(namespace, method)
            LOG.debug('Rpc cast can not find endpoint %s, method %s not called' % (namespace, method))
        except exceptions.MessageNotForMe:
            LOG.debug('Dispatch find meassage not for this agent')
        except exceptions.ExpectedException as e:
            LOG.debug('Expected exception during message handling (%s)' % str(e.exc_info[1]))
            incoming.reply(failure=e.exc_info, log_failure=False)
        except Exception as e:
            exc_info = sys.exc_info()
            try:
                LOG.error('Exception during message handling: %s %s' % (e.__class__.__name__, e))
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
        self._dispatch(self._incoming)
        # try:
        #     self._dispatch(self._incoming)
        # except Exception:
        #     msg = 'The dispatcher method must catches all exceptions'
        #     LOG.exception(msg)
        #     raise RuntimeError(msg)

    def done(self, *args, **kwargs):
        pass
