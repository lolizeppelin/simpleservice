from simpleservice import common

class ConfigNotFound(Exception):
    def __init__(self, path):
        msg = 'Could not find config at %(path)s' % {'path': path}
        super(ConfigNotFound, self).__init__(msg)


class PasteAppNotFound(Exception):
    def __init__(self, name, path):
        msg = ("Could not load paste app '%(name)s' from %(path)s" %
               {'name': name, 'path': path})
        super(PasteAppNotFound, self).__init__(msg)


class NoFaultsKonwnExcpetion(Exception):
    """Not any Konwn Excpetion found"""


class HttpRequestError(Exception):
    """Base http request error"""


class BeforeRequestError(HttpRequestError):
    """Error before send request"""


class ConnectionFailed(HttpRequestError):
    """Send http request get socket error"""


class AfterRequestError(HttpRequestError):

    def __init__(self, message,
                 code=0, resone='unkonwon error'):
        self.message = message
        self.code = code
        self.resone = resone


class ServerNotImplementedError(AfterRequestError):
    """Server Not Implemented request"""
    def __init__(self, message='Request not implemented',
                 code=501, resone='unkonwon'):
        super(ServerNotImplementedError, self).__init__(message, code, resone)


class ClientRequestError(AfterRequestError):
    """Client error, miss some argvment?"""


class ServerExecuteRequestError(AfterRequestError):
    """Request send success, action execute fail"""
    def __init__(self, message='Server execute request fail',
                 code=0, resone='unkonwon error'):
        super(ServerExecuteRequestError, self).__init__(message, code, resone)


class DeserializeRequestError(AfterRequestError):
    """Serialize request body fail"""
    def __init__(self, message='Deserialize respone data fail',
                 code=common.DESERIALIZE_FAIL, resone='unkonwon buffer'):
        super(DeserializeRequestError, self).__init__(message, code, resone)


class ServerRsopneCodeError(AfterRequestError):
    def __init__(self, message='Server rsopne http code out of range',
                 code=0, resone='unkonwon resone'):
        super(ServerRsopneCodeError, self).__init__(message, code, resone)
