import sys
import copy
import six
import collections
import uuid
import traceback

from simpleutil.log import log as logging
from simpleutil.utils import jsonutils
from simpleutil.utils import timeutils

from simpleservice.rpc.driver import exceptions

PURPOSE_LISTEN = 'listen'
PURPOSE_SEND = 'send'
_REMOTE_POSTFIX = '_Remote'
UNIQUE_ID = '_unique_id'

_EXCEPTIONS_MODULE = 'exceptions' if six.PY2 else 'builtins'

LOG = logging.getLogger(__name__)

MsgTimeoutRecorder = None

def _add_unique_id(msg):
    """Add unique_id for checking duplicate messages."""
    unique_id = uuid.uuid4().hex
    msg.update({UNIQUE_ID: unique_id})


def serialize_msg(raw_msg):
    # NOTE(russellb) See the docstring for _RPC_ENVELOPE_VERSION for more
    # information about this format.
    msg = jsonutils.dumps(raw_msg)
    return msg


def deserialize_msg(msg):
    # if not isinstance(msg, dict):
    if isinstance(msg, dict):
        # See #2 above.
        return msg
    return jsonutils.loads(msg)


def serialize_remote_exception(failure_info, log_failure=True):
    """Prepares exception data to be sent over rpc.

    Failure_info should be a sys.exc_info() tuple.

    """
    tb = traceback.format_exception(*failure_info)
    failure = failure_info[1]
    if log_failure:
        LOG.error("Returning exception %s to caller",
                  six.text_type(failure))
        LOG.error(tb)

    kwargs = {}
    if hasattr(failure, 'kwargs'):
        kwargs = failure.kwargs

    # NOTE(matiu): With cells, it's possible to re-raise remote, remote
    # exceptions. Lets turn it back into the original exception type.
    cls_name = six.text_type(failure.__class__.__name__)
    mod_name = six.text_type(failure.__class__.__module__)
    if (cls_name.endswith(_REMOTE_POSTFIX) and
            mod_name.endswith(_REMOTE_POSTFIX)):
        cls_name = cls_name[:-len(_REMOTE_POSTFIX)]
        mod_name = mod_name[:-len(_REMOTE_POSTFIX)]

    data = {
        'class': cls_name,
        'module': mod_name,
        'message': six.text_type(failure),
        'tb': tb,
        'args': failure.args,
        'kwargs': kwargs
    }
    json_data = jsonutils.dumps(data)
    return json_data


def deserialize_remote_exception(data, allowed_remote_exmods):
    failure = jsonutils.loads(six.text_type(data))

    trace = failure.get('tb', [])
    message = failure.get('message', "") + "\n" + "\n".join(trace)
    name = failure.get('class')
    module = failure.get('module')

    # NOTE(ameade): We DO NOT want to allow just any module to be imported, in
    # order to prevent arbitrary code execution.
    if module != _EXCEPTIONS_MODULE and module not in allowed_remote_exmods:
        return exceptions.RemoteError(name, failure.get('message'), trace)

    try:
        __import__(module)
        mod = sys.modules[module]
        klass = getattr(mod, name)
        if not issubclass(klass, Exception):
            raise TypeError("Can only deserialize Exceptions")

        failure = klass(*failure.get('args', []), **failure.get('kwargs', {}))
    except (AttributeError, TypeError, ImportError):
        return exceptions.RemoteError(name, failure.get('message'), trace)

    ex_type = type(failure)
    str_override = lambda self: message
    new_ex_type = type(ex_type.__name__ + _REMOTE_POSTFIX, (ex_type,),
                       {'__str__': str_override, '__unicode__': str_override})
    new_ex_type.__module__ = '%s%s' % (module, _REMOTE_POSTFIX)
    try:
        # NOTE(ameade): Dynamically create a new exception type and swap it in
        # as the new type for the exception. This only works on user defined
        # Exceptions and not core Python exceptions. This is important because
        # we cannot necessarily change an exception message so we must override
        # the __str__ method.
        failure.__class__ = new_ex_type
    except TypeError:
        # NOTE(ameade): If a core exception then just add the traceback to the
        # first exception argument.
        failure.args = (message,) + failure.args[1:]
    return failure


def pack_context(msg, context):
    """Pack context into msg.

    Values for message keys need to be less than 255 chars, so we pull
    context out into a bunch of separate keys. If we want to support
    more arguments in rabbit messages, we may want to do the same
    for args at some point.

    """
    if isinstance(context, dict):
        context_d = six.iteritems(context)
    else:
        context_d = six.iteritems(context.to_dict())

    msg.update(('_context_%s' % key, value)
               for (key, value) in context_d)


def unpack_context(msg):
    """Unpack context from msg."""
    context_dict = {}
    for key in list(msg.keys()):
        key = six.text_type(key)
        if key.startswith('_context_'):
            value = msg.pop(key)
            context_dict[key[9:]] = value
    context_dict['msg_id'] = msg.pop('_msg_id', None)
    context_dict['reply_q'] = msg.pop('_reply_q', None)
    context_dict['request_id'] = msg.pop('_request_id', None)
    return RpcContext.from_dict(context_dict)


class RpcContext(object):
    """Context that supports replying to a rpc.call."""
    def __init__(self, **kwargs):
        self.msg_id = kwargs.pop('msg_id', None)
        self.reply_q = kwargs.pop('reply_q', None)
        self.request_id = kwargs.pop('request_id', None)
        self.values = kwargs

    def __getattr__(self, key):
        try:
            return self.values[key]
        except KeyError:
            raise AttributeError(key)

    def to_dict(self):
        return copy.deepcopy(self.values)

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def deepcopy(self):
        values = self.to_dict()
        values['msg_id'] = self.msg_id
        values['reply_q'] = self.reply_q
        values['request_id'] = self.request_id
        return self.__class__(**values)


class _MsgIdCache(object):
    """This class checks any duplicate messages."""

    # NOTE: This value is considered can be a configuration item, but
    #       it is not necessary to change its value in most cases,
    #       so let this value as static for now.
    DUP_MSG_CHECK_SIZE = 16

    # def __init__(self, **kwargs):
    def __init__(self):
        self.prev_msgids = collections.deque([],
                                             maxlen=self.DUP_MSG_CHECK_SIZE)

    def check_duplicate_message(self, message_data):
        """AMQP consumers may read same message twice when exceptions occur
           before ack is returned. This method prevents doing it.
        """
        try:
            msg_id = message_data.pop(UNIQUE_ID)
        except KeyError:
            return
        if msg_id in self.prev_msgids:
            raise exceptions.DuplicateMessageError(msg_id=msg_id)
        return msg_id

    def add(self, msg_id):
        if msg_id and msg_id not in self.prev_msgids:
            self.prev_msgids.append(msg_id)


class DecayingTimer(object):
    def __init__(self, duration=None):
        self._watch = timeutils.StopWatch(duration=duration)

    def start(self):
        self._watch.start()

    def check_return(self, timeout_callback=None, *args, **kwargs):
        maximum = kwargs.pop('maximum', None)
        left = self._watch.leftover(return_none=True)
        if left is None:
            return maximum
        if left <= 0 and timeout_callback is not None:
            timeout_callback(*args, **kwargs)
        return left if maximum is None else min(left, maximum)
