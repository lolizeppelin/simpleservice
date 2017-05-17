from simpleservice.plugin.endpoint.wsgi.scheduler.routers import Routers as scheduler_routes


from simpleservice.plugin.manager.rpc.base import ManagerBase
from simpleservice.plugin.manager.wsgi.agent.routers import Routers as agent_routes
from simpleservice.plugin.manager.wsgi.asyncrequest.routers import Routers as request_routes

core_routes = [request_routes, agent_routes, scheduler_routes]