import sys
import six

from simpleutil.log import log as logging

LOG = logging.getLogger(__name__)


class MessageNotForMe(Exception):
    """rpc not for this this agent"""


class AMQPDestinationNotFound(Exception):
    pass


class RPCException(Exception):
    msg_fmt = "An unknown RPC related exception occurred."

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if not message:
            try:
                message = self.msg_fmt % kwargs
            except Exception:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception('Exception in string format operation, kwargs are:')
                for name, value in six.iteritems(kwargs):
                    LOG.error("%s: %s", name, value)
                # at least get the core message out if something happened
                message = self.msg_fmt

        super(RPCException, self).__init__(message)


class Timeout(RPCException):
    """Signifies that a timeout has occurred.

    This exception is raised if the rpc_response_timeout is reached while
    waiting for a response from the remote side.
    """
    msg_fmt = 'Timeout while waiting on RPC response - ' \
              'topic: "%(topic)s", RPC method: "%(method)s" ' \
              'info: "%(info)s"'

    def __init__(self, info=None, topic=None, method=None):
        """Initiates Timeout object.

        :param info: Extra info to convey to the user
        :param topic: The topic that the rpc call was sent to
        :param method: The name of the rpc method being
                                called
        """
        self.info = info
        self.topic = topic
        self.method = method
        super(Timeout, self).__init__(
            None,
            info=info or '<unknown>',
            topic=topic or '<unknown>',
            method=method or '<unknown>')


class InvalidRPCConnectionReuse(RPCException):
    msg_fmt = "Invalid reuse of an RPC connection."


class DuplicateMessageError(RPCException):
    msg_fmt = "Found duplicate message(%(msg_id)s). Skipping it."


class MessagingException(Exception):
    """Base class for exceptions."""


class MessagingTimeout(MessagingException):
    """Raised if message sending times out."""


class MessageDeliveryFailure(MessagingException):
    """Raised if message sending failed after the asked retry."""


class RemoteError(MessagingException):

    """Signifies that a remote endpoint method has raised an exception.

    Contains a string representation of the type of the original exception,
    the value of the original exception, and the traceback.  These are
    sent to the parent as a joined string so printing the exception
    contains all of the relevant info.
    """

    def __init__(self, exc_type=None, value=None, traceback=None):
        self.exc_type = exc_type
        self.value = value
        self.traceback = traceback
        msg = ("Remote error: %(exc_type)s %(value)s\n%(traceback)s." %
               dict(exc_type=self.exc_type, value=self.value,
                    traceback=self.traceback))
        super(RemoteError, self).__init__(msg)


class RPCVersionCapError(MessagingException):

    def __init__(self, version, version_cap):
        self.version = version
        self.version_cap = version_cap
        msg = ("Requested message version, %(version)s is incompatible.  It "
               "needs to be equal in major version and less than or equal "
               "in minor version as the specified version cap "
               "%(version_cap)s." %
               dict(version=self.version, version_cap=self.version_cap))
        super(RPCVersionCapError, self).__init__(msg)


class RpcClientSendError(MessagingException):
    """Raised if we failed to send a message to a target."""

    def __init__(self, target, ex):
        msg = 'Failed to send to target "%s": %s' % (target, ex)
        super(RpcClientSendError, self).__init__(msg)
        self.target = target
        self.ex = ex


class InvalidTarget(MessagingException, ValueError):
    """Raised if a target does not meet certain pre-conditions."""

    def __init__(self, msg, target):
        msg = msg + ":" + six.text_type(target)
        super(InvalidTarget, self).__init__(msg)
        self.target = target


# TransportDriverError
class RabbitDriverError(MessagingException):
    """Base class for transport driver specific exceptions."""


class MessagingServerError(MessagingException):
    """Base class for all MessageHandlingServer exceptions."""


class TaskTimeout(MessagingServerError):
    """Raised if we timed out waiting for a task to complete."""


class RPCDispatcherError(MessagingServerError):
    """A base class for all RPC dispatcher exceptions."""


class NoSuchMethod(RPCDispatcherError, AttributeError):
    """Raised if no Method found"""


class EndpointNoSuchMethod(NoSuchMethod):
    """Raised if there is no endpoint which exposes the requested method."""

    def __init__(self, namespace, method):
        msg = "Endpoint %s does not support RPC method %s" % (namespace, method)
        super(EndpointNoSuchMethod, self).__init__(msg)
        self.method = method


class ManagerNoSuchMethod(NoSuchMethod):
    """Raised if there is no endpoint which exposes the requested method."""

    def __init__(self, method):
        msg = "Manager does not support RPC method %s" % method
        super(ManagerNoSuchMethod, self).__init__(msg)
        self.method = method


class UnsupportedNamespace(RPCDispatcherError):
    """Raised if there is no endpoint which supports the requested version."""
    def __init__(self, namespace, method=None):
        msg = "Endpoint does not support RPC namespace %s" % namespace
        if method:
            msg = "%s. Attempted method: %s" % (msg, method)
        super(UnsupportedNamespace, self).__init__(msg)
        self.namespace = namespace
        self.method = method


class ExpectedException(Exception):
    """Encapsulates an expected exception raised by an RPC endpoint

    Merely instantiating this exception records the current exception
    information, which  will be passed back to the RPC client without
    exceptional logging.
    """
    def __init__(self):
        self.exc_info = sys.exc_info()
