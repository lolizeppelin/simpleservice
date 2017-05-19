from simpleservice.ormdb import orm
from simpleservice.ormdb.tools.utils import init_database

from simpleservice.plugin.models import PluginTableBase
from simpleservice.plugin.models import GkeyMap

from simpleservice.plugin.manager import models as manager_models
from simpleservice.plugin.endpoint import models as endpoint_models


def init_plugin_data(engine):
    session_maker = orm.get_maker(engine=engine)
    session = session_maker()
    with session.begin():
        # Start from 1
        for i in xrange(1, 2048):
            row = GkeyMap(sid=i, host=None)
            session.add(row)
    if hasattr(manager_models, 'init_data'):
        getattr(manager_models, 'init_data')(session)
    if hasattr(endpoint_models, 'init_data'):
        getattr(endpoint_models, 'init_data')(session)
    session.close()


def init_plugin_database(db_info, init_data_func=init_plugin_data):
    init_database(db_info, metadata=PluginTableBase.metadata,
                  init_data_func=init_data_func)