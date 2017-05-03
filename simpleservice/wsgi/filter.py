# -*- coding: UTF-8 -*-
import abc

import webob.dec
import webob.exc


class FilterBase(object):
    NAME = 'FilterBase'

    @classmethod
    def factory(cls, global_conf, **local_conf):
        """Factory method for paste.deploy.

        :param global_conf: dict of options for all middlewares
                            (usually the [DEFAULT] section of the paste deploy
                            configuration file)
        :param local_conf: options dedicated to this middleware
                           (usually the option defined in the middleware
                           section of the paste deploy configuration file)
        """
        conf = global_conf.copy() if global_conf else {}
        conf.update(local_conf)

        def middleware_filter(app):
            return cls(app)

        return middleware_filter

    def __init__(self, application):
        self.application = application

    @abc.abstractmethod
    def process_request(self, req):
        """Called on each request.
        If this returns None, the next application down the stack will be
        executed. If it returns a response then that response will be returned
        and execution will stop here.
        返回对象可以是Response实例
        webob将会直接直接调用这个Response实例的__call__方法
        返回对象可以是文本对象
        webob将通过req.Response类生成Response实例再调用__call__方法
        返回值不是None表明过滤失败
        """

    def process_response(self, req, response):
        """Do whatever you'd like to the response, based on the request."""
        return response

    @webob.dec.wsgify()
    def __call__(self, req):
        response = self.process_request(req)
        if response:
            return response
        response = req.get_response(self.application)
        return self.process_response(req, response)