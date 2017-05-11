import time
s = time.time()
from simpleservice.ormdb.argformater import template

print time.time() - s

print template.slave_connection, type(template.slave_connection)
print template.connection, type(template.connection)
print template.mysql_sql_mode