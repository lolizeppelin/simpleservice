from simpleservice.ormdb import orm
from simpleservice.ormdb.tools.utils import init_database

from simpleservice.plugin.manager.models import ManagerTableBase
from simpleservice.plugin.manager.models import GkeyMap

def init_manager_data(engine):
        session_maker = orm.get_maker(engine=engine)
        session = session_maker()
        with session.begin():
            for i in xrange(0, 2048):
                row = GkeyMap(sid=i)
                session.add(row)
        session.close()


def init_manager_database(db_info):
    init_database(db_info, ManagerTableBase.metadata, init_manager_data)