import eventlet
import sys
reload(sys)
from simpleutil import system


if system.WINDOWS:
    # eventlet monkey patching the os and thread modules causes
    # subprocess.Popen to fail on Windows when using pipes due
    # to missing non-blocking IO support.
    #
    # bug report on eventlet:
    # https://bitbucket.org/eventlet/eventlet/issue/132/
    #       eventletmonkey_patch-breaks
    sys.setdefaultencoding('gb2312')
    eventlet.monkey_patch(os=False, thread=False)
    import amqp.transport
    import socket
    # Remove TCP_MAXSEG, Avoid koumbu raise socket error on windows
    opt_name = 'TCP_MAXSEG'
    opt_id = getattr(socket, 'TCP_MAXSEG')
    if opt_id and opt_id in amqp.transport.TCP_OPTS:
        amqp.transport.TCP_OPTS.remove(opt_id)
    if opt_name in amqp.transport.KNOWN_TCP_OPTS:
        amqp.transport.KNOWN_TCP_OPTS = list(amqp.transport.KNOWN_TCP_OPTS)
        amqp.transport.KNOWN_TCP_OPTS.remove(opt_name)
        amqp.transport.KNOWN_TCP_OPTS = tuple(amqp.transport.KNOWN_TCP_OPTS)
    # import eventlet.debug
    # eventlet.debug.hub_prevent_multiple_readers(False)
else:
    eventlet.monkey_patch()
    sys.setdefaultencoding('utf-8')
