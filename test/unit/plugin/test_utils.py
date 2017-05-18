from simpleservice.plugin import utils

dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'manager',
       'user': 'root',
       'passwd': '111111'}

utils.init_plugin_database(dst)