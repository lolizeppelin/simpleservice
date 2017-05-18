from simpleservice.wsgi import router


from simpleservice.plugin.manager.wsgi.asyncrequest import controller

MEMBER_ACTIONS = ['show']
COLLECTION_ACTIONS = ['index']


class Routers(router.RoutersBase):
    collection_name = 'schdulers'
    resource_name='schduler'

    pass