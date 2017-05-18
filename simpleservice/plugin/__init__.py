from simpleservice.plugin.manager.rpc.base import ManagerBase

from simpleservice.plugin.manager.wsgi.agent import routers as agent_routes
from simpleservice.plugin.manager.wsgi.asyncrequest import routers as request_routes
from simpleservice.plugin.endpoint.wsgi.scheduler import routers as scheduler_routes

CORE_ROUTES = [request_routes, agent_routes, scheduler_routes]