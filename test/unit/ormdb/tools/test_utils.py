from simpleservice.ormdb.tools.utils import init_database

from simpleservice.plugin.models import PluginTableBase

dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'manager',
       'user': 'root',
       'passwd': '111111'}

init_database(dst, PluginTableBase.metadata)