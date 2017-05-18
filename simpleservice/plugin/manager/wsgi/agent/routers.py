from simpleservice.wsgi import router
from simpleservice.wsgi import controller_return_response

from simpleservice.plugin.manager.wsgi.asyncrequest import controller

MEMBER_ACTIONS = ['show']
COLLECTION_ACTIONS = ['index']


class Routers(router.RoutersBase):
    collection_name = 'agents'
    resource_name='agent'