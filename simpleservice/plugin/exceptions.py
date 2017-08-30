from simpleservice import common


class HttpRequestError(Exception):
    """Base http request error"""


class ConnectionFailed(HttpRequestError):
    """Send http request get socket error"""


class BeforeRequestError(HttpRequestError):
    """Error before send request"""


class AfterRequestError(HttpRequestError):

    def __init__(self, message='Get error after request',
                 code=0, resone='unkonwon error'):
        self.message = message
        self.code = code
        self.resone = resone


class ClientRequestError(AfterRequestError):
    """Client error, miss some argvment?"""
    def __init__(self, message='Server retrun a client error',
                 code=400, resone='unkonwon'):
        super(ClientRequestError, self).__init__(message, code, resone)


class ServerInternalError(AfterRequestError):
    """Request send success, server internal error"""
    def __init__(self, message='Server internal error',
                 code=500, resone='unkonwon error'):
        super(ServerInternalError, self).__init__(message, code, resone)


class ServerNotImplementedError(AfterRequestError):
    """Server Not Implemented request"""
    def __init__(self, message='Request not implemented',
                 code=501, resone='unkonwon'):
        super(ServerNotImplementedError, self).__init__(message, code, resone)


class DeserializeRequestError(AfterRequestError):
    """Serialize request body fail"""
    def __init__(self, message='Deserialize respone data fail',
                 code=200, resone='unkonwon buffer'):
        super(DeserializeRequestError, self).__init__(message, code, resone)


class ServerExecuteRequestError(AfterRequestError):
    """Request send success, action execute fail"""
    def __init__(self, message='Server execute request fail',
                 code=200, resone='unkonwon error'):
        super(ServerExecuteRequestError, self).__init__(message, code, resone)


class ServerRsopneCodeError(AfterRequestError):
    def __init__(self, message='Server respone http code out of range',
                 code=common.RESULT_UNKNOWN, resone='unkonwon resone'):
        super(ServerRsopneCodeError, self).__init__(message, code, resone)
