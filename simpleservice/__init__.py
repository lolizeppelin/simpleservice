import os
import eventlet
import sys
reload(sys)


if os.name == 'nt':
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
    # Remove TCP_MAXSEG, or,  koumbu will raise socket error
    opt_name = 'TCP_MAXSEG'
    opt_id = getattr(socket, 'TCP_MAXSEG')
    amqp.transport.TCP_OPTS.remove(opt_id)
    amqp.transport.KNOWN_TCP_OPTS = list(amqp.transport.KNOWN_TCP_OPTS)
    amqp.transport.KNOWN_TCP_OPTS.remove(opt_name)
    amqp.transport.KNOWN_TCP_OPTS = tuple(amqp.transport.KNOWN_TCP_OPTS)
    # import eventlet.debug
    # eventlet.debug.hub_prevent_multiple_readers(False)
else:
    eventlet.monkey_patch()
    sys.setdefaultencoding('utf-8')
