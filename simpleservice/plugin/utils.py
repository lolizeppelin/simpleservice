from simpleservice.ormdb import orm
from simpleservice.ormdb.tools.utils import init_database
from simpleservice.plugin.models import GkeyMap
from simpleservice.plugin.models import PluginTableBase


def init_plugin_database(db_info, *models):
    """Table in models must base on PluginTableBase
    So that table in models can be carete when call init_database
    """
    def init_plugin_data(engine):
        session_maker = orm.get_maker(engine=engine)
        session = session_maker()
        # with session.begin():
            # Start from 1
            # So 1-2047 can be used as gkey id
        for i in xrange(1, 2048):
            row = GkeyMap(sid=i, host=None)
            session.add(row)
            session.flush()
        for _models in models:
            if hasattr(_models, 'init_data'):
                getattr(_models, 'init_data')(session)
        session.close()
    init_database(db_info, metadata=PluginTableBase.metadata,
                  init_data_func=init_plugin_data)
