# -*- coding: UTF-8 -*-
import webob.dec
import webob.exc

from sqlalchemy.exc import SQLAlchemyError

from simpleutil.log import log as logging
from simpleutil.utils import jsonutils
from simpleutil.utils import systemutils

from simpleservice.ormdb.exceptions import DBError
from simpleservice.wsgi.exceptions import NoFaultsKonwnExcpetion


LOG = logging.getLogger(__name__)

DEFAULT_CONTENT_TYPE = 'application/json'
STREAM_CONTENT_TYPE = 'application/octet-stream'

deserializers = {
    DEFAULT_CONTENT_TYPE: jsonutils.loads_as_bytes,
    STREAM_CONTENT_TYPE: lambda x: x
}

serializers = {
    DEFAULT_CONTENT_TYPE: jsonutils.dumps_as_bytes,
    STREAM_CONTENT_TYPE: lambda x: x
}

default_serializer = serializers[DEFAULT_CONTENT_TYPE]


class MiddlewareContorller(object):

    @property
    def absname(self):
        # 类具体位置和名称,用于记录错误模块
        return '%s.%s' % (self.__module__, self.__class__.__name__)


def controller_return_response(controller, faults=None, action_status=None):
    """Represents an API entity resource and the associated serialization and
    deserialization logic
    """
    if not isinstance(controller, MiddlewareContorller):
        raise TypeError('%s.%s is not base from MiddlewareContorller' % (controller.__module__,
                                                                         controller.__class__.__name__))
    ctrl_name = controller.absname
    # action_status = action_status or dict(create=201, delete=204)
    action_status = action_status or dict()
    faults = faults or {}
    # 已知错误
    konwn_exceptions = tuple(faults.keys() if faults else NoFaultsKonwnExcpetion) if faults else tuple()

    @webob.dec.wsgify()
    def resource(req):
        # wsgi.Router的_dispatch通过match找到contorler
        # 在调用contorler(req)
        # 这里就是被调用的那个contorler
        match = req.environ['wsgiorg.routing_args'][1]
        args = match.copy()
        # 弹出的controller
        args.pop('controller', None)
        args.pop('format', None)
        action = args.pop('action', '__call__')
        content_type = req.content_type
        try:
            # content_type = DEFAULT_CONTENT_TYPE
            deserializer = deserializers[content_type]
            serializer = serializers[content_type]
        except KeyError:
            body = default_serializer({'msg': 'can not find %s deserializer' % req.content_type})
            kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
            raise webob.exc.HTTPNotImplemented(**kwargs)
        if req.body:
            try:
                args['body'] = deserializer(req.body)
            except TypeError:
                body = default_serializer({'msg': 'HTTPClientError, body cannot be deserializer'})
                kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
                raise webob.exc.HTTPClientError(**kwargs)
        LOG.debug('PID:%d Middleware Route destination %s:%s' %
                  (systemutils.PID, ctrl_name, action), resource=None)
        try:
            # controller是自由变量
            # 这个controller是外部传入的controller
            method = getattr(controller, action)
            result = method(req, **args)
        except konwn_exceptions as e:
            mapped_exc = faults[e.__class__]
            if 400 <= mapped_exc.code < 500:
                LOG.info('%(action)s failed (client error): %(exc)s',
                         {'action': action, 'exc': e})
            else:
                LOG.error('%s:%s failed' % (ctrl_name, action))
            body = default_serializer({'msg': '%s: %s' % (e.__class__.__name__, e.message)})
            kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
            raise mapped_exc(**kwargs)
        except NotImplementedError as e:
            body = default_serializer({'msg': 'Request Failed: NotImplementedError %s' % e.message})
            kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
            LOG.error('%s:%s failed %s' % (ctrl_name, action, e.message))
            raise webob.exc.HTTPNotImplemented(**kwargs)
        except webob.exc.HTTPException as e:
            # type_, value, tb = sys.exc_info()
            if not isinstance(e, webob.Response):
                msg = e.message if hasattr(e, 'message') and e.message else 'unkonwon'
                msg = 'Request Failed: HTTPException Reson: %s' % msg
                LOG.error('%s failed %s' % (action, msg))
                body = default_serializer({'msg': msg})
                kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
                raise webob.exc.HTTPInternalServerError(**kwargs)
            if hasattr(e, 'code') and 400 <= e.code < 500:
                msg = '%(action)s failed (client error): %(exc)s' % {'action': action, 'exc': e}
                LOG.info(msg)
            else:
                msg = '%s:%s failed' % (ctrl_name, action)
                LOG.error(msg)
            msg = 'Request Failed: HTTPException on %s' % msg
            e.body = default_serializer({'msg': msg})
            e.content_type = DEFAULT_CONTENT_TYPE
            raise e
        except jsonutils.ValidationError as e:
            if LOG.isEnabledFor(logging.DEBUG):
                LOG.exception('%s failed', action)
            else:
                LOG.error('%s:%s failed, json validate fail', (ctrl_name, action))
            msg = e.message.replace('"', ' ')
            if e.path:
                msg = '%s value %s' % ('.'.join(e.path), msg)
            msg = 'Request Failed: json not match, %s' % msg
            body = default_serializer({'msg': msg})
            kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
            raise webob.exc.HTTPClientError(**kwargs)
        except (SQLAlchemyError, DBError):
            # Database error details will not send
            if LOG.isEnabledFor(logging.DEBUG):
                LOG.exception('%s failed', action)
            else:
                LOG.error('%s:%s failed, database exception', (ctrl_name, action))
            # Do not expose details of database error to clients.
            msg = 'Request Failed: internal server error while ' \
                  'reading or writing database'
            body = default_serializer({'msg': msg})
            kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
            raise webob.exc.HTTPInternalServerError(**kwargs)
        except Exception as e:
            # NOTE(jkoelker) Everything else is 500
            if LOG.isEnabledFor(logging.DEBUG):
                LOG.exception('MiddlewareContorller unexpect exception on %s' % action)
            else:
                LOG.error('%s:%s failed, unkonwn exception', (ctrl_name, action))
            # Do not expose details of 500 error to clients.
            msg = 'Request Failed: internal server error while ' \
                  'processing your request. %(class)s, %(message)s' % \
                  {'class': e.__class__.__name__, 'message': e.message}
            body = default_serializer({'msg': msg})
            kwargs = {'body': body, 'content_type': DEFAULT_CONTENT_TYPE}
            raise webob.exc.HTTPInternalServerError(**kwargs)
        status = action_status.get(action, 200)
        body = serializer(result)
        # NOTE(jkoelker) Comply with RFC2616 section 9.7
        if status == 204:
            body = None
        # 返回对象是Response实例
        # response的时候直接调用这个Response实例的__call__方法
        # environ是req.environ
        # 这里的start_response是eventlet.wsgi.handle_one_response中的闭包start_response
        # 这里模拟的是neutron里的写法
        # keyston的controller不会通过闭包返回Response类
        # keyston的controller会直接返回文本
        # 当返回文本对象的时候会先通过req.Response类生成Response实例
        # 再调用__call__方法
        # 有必要会设置req.Response类指向一个继承webob.Response的类
        return webob.Response(request=req, status=status,
                              content_type=content_type,
                              body=body)
    # 返回闭包
    return resource
