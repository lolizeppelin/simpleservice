from simpleservice.ormdb.tools.utils import init_manager_database

from simpleservice.plugin.manager.models import ManagerTableBase

dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'manager',
       'user': 'root',
       'passwd': '111111'}

init_manager_database(dst, ManagerTableBase)
