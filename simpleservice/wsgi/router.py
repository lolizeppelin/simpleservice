# -*- coding: UTF-8 -*-
import six
import abc

import webob.dec
import webob.exc

import routes.middleware


class Router(object):
    """WSGI middleware that maps incoming requests to WSGI apps."""

    def __init__(self, mapper):
        """Create a router for the given routes.Mapper.

        Each route in `mapper` must specify a 'controller', which is a
        WSGI app to call.  You'll probably want to specify an 'action' as
        well and have your controller be an object that can route
        the request to the action-specific method.

        Examples:
          mapper = routes.Mapper()
          sc = ServerController()

          # Explicit mapping of one route to a controller+action
          mapper.connect(None, '/svrlist', controller=sc, action='list')

          # Actions are all implicitly defined
          mapper.resource('server', 'servers', controller=sc)

          # Pointing to an arbitrary WSGI app.  You can specify the
          # {path_info:.*} parameter so the target app can be handed just that
          # section of the URL.
          mapper.connect(None, '/v1.0/{path_info:.*}', controller=BlogApp())

        """
        self.map = mapper
        self._router = routes.middleware.RoutesMiddleware(self._dispatch,
                                                          self.map)

    @webob.dec.wsgify()
    def __call__(self, req):
        """Route the incoming request to a controller based on self.map.

        If no match, return a 404.

        """
        return self._router

    @staticmethod
    @webob.dec.wsgify()
    def _dispatch(req):
        """Dispatch the request to the appropriate controller.

        Called by self._router after matching the incoming request to a route
        and putting the information into req.environ.  Either returns 404
        or the routed WSGI app's response.

        """
        match = req.environ['wsgiorg.routing_args'][1]
        if not match:
            return webob.exc.HTTPNotFound()
        app = match['controller']
        return app


@six.add_metaclass(abc.ABCMeta)
class ComposableRouter(Router):
    """Router that supports use by ComposingRouter.
    组件路由,mapper.connect具体调用
    这个类要继承重写
    """

    def __init__(self, mapper=None):
        if mapper is None:
            mapper = routes.Mapper()
        self.add_routes(mapper)
        super(ComposableRouter, self).__init__(mapper)

    @abc.abstractmethod
    def add_routes(self, mapper):
        """Add routes to given mapper.
        这里写具体mapper.connect调用,例如
        mapper.connect('action_name', # some action join self.resource_name with "_"
                       path='/%s/{id}/action' % self.collection_name,
                       controller=controller_intance, action='action_function_name',
                       conditions=dict(method=['HEAD']))
        """


class ComposingRouter(Router):
    """路由组装器/组装工厂, 将ComposableRouter类实例"组装"起来
    组装过程就是调用ComposableRouter类实例的add_routes方法
    """
    def __init__(self, mapper=None, routers=None):
        if mapper is None:
            mapper = routes.Mapper()
        if routers is None:
            routers = []
        for router in routers:
            router.add_routes(mapper)
        super(ComposingRouter, self).__init__(mapper)


@six.add_metaclass(abc.ABCMeta)
class RoutersBase(object):
    """Base class for Routers."""

    resource_name = 'unkonwn'

    def __init__(self):
        self.resources = []

    @abc.abstractmethod
    def append_routers(self, mapper, routers=None):
        """Append routers.
        Subclasses should override this method to map its routes.
        添加路由有三种实现方式

        1、直接在当前函数中写mapper.connect、mapper.collection等
           neutron里使用这种方式
        2、将生成的路由(继承自ComposableRouter)添加到routers(参数)这个列表中,
           外部会一次性用ComposingRouter组装routers列表中的所有路由
           这个方式一般是让路由延后加载,keystone有部分路由使用这个方式
        3、调用下面的_add_resource生成路由(里面封装了mapper.connect)
           这个方式keystone里用得比较多
        """

    def _add_resource(self, mapper, controller, path,
                      get_action=None, head_action=None, get_head_action=None,
                      put_action=None, post_action=None, patch_action=None,
                      delete_action=None, get_post_action=None):
        if get_head_action:
            # getattr(controller, get_head_action)
            mapper.connect(get_head_action + '_' + self.resource_name,
                           path, controller=controller, action=get_head_action,
                           conditions=dict(method=['GET', 'HEAD']))
        if get_action:
            # getattr(controller, get_action)
            mapper.connect(get_action + '_' + self.resource_name,
                           path, controller=controller, action=get_action,
                           conditions=dict(method=['GET']))
        if head_action:
            # getattr(controller, head_action)
            mapper.connect(head_action + '_' + self.resource_name,
                           path, controller=controller, action=head_action,
                           conditions=dict(method=['HEAD']))
        if put_action:
            # getattr(controller, put_action)
            mapper.connect(put_action + '_' + self.resource_name,
                           path, controller=controller, action=put_action,
                           conditions=dict(method=['PUT']))
        if post_action:
            # getattr(controller, post_action)
            mapper.connect(post_action + '_' + self.resource_name,
                           path, controller=controller, action=post_action,
                           conditions=dict(method=['POST']))
        if patch_action:
            # getattr(controller, patch_action)
            mapper.connect(patch_action + '_' + self.resource_name,
                           path, controller=controller, action=patch_action,
                           conditions=dict(method=['PATCH']))
        if delete_action:
            # getattr(controller, delete_action)
            mapper.connect(delete_action + '_' + self.resource_name,
                           path, controller=controller, action=delete_action,
                           conditions=dict(method=['DELETE']))
        if get_post_action:
            # getattr(controller, get_post_action)
            mapper.connect(get_post_action + '_' + self.resource_name,
                           path, controller=controller, action=get_post_action,
                           conditions=dict(method=['GET', 'POST']))
