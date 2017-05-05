import os
import eventlet


if os.name == 'nt':
    # eventlet monkey patching the os and thread modules causes
    # subprocess.Popen to fail on Windows when using pipes due
    # to missing non-blocking IO support.
    #
    # bug report on eventlet:
    # https://bitbucket.org/eventlet/eventlet/issue/132/
    #       eventletmonkey_patch-breaks
    eventlet.monkey_patch(os=False, thread=False)
else:
    eventlet.monkey_patch()
