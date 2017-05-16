from simpleservice.wsgi import router
from simpleservice.wsgi import controller_return_response

from simpleservice.plugin.manager.wsgi.asyncrequest import controller

MEMBER_ACTIONS = ['show']
COLLECTION_ACTIONS = ['index']


class Routers(router.RoutersBase):
    collection_name = 'asyncrequests'
    resource_name='asyncrequest'

    def append_routers(self, mapper, routers):
        controller_intance = controller_return_response(controller.AsyncWorkRequest(),
                                                        controller.FAULT_MAP)
        collection = mapper.collection(collection_name=self.collection_name,
                                       resource_name=self.resource_name,
                                       controller=controller_intance,
                                       member_prefix='/{request_id}',
                                       collection_actions=COLLECTION_ACTIONS,
                                       member_actions=MEMBER_ACTIONS)
        # collection.member.link(rel='active', action='active', method='POST')
        return collection