from simpleservice.plugin.manager import utils



dst = {'host': '172.20.0.3',
       'port': 3304,
       'schema': 'manager',
       'user': 'root',
       'passwd': '111111'}

utils.init_manager_database(dst)