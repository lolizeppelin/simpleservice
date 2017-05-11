
import logging



from simpleservice.ormdb.tools import copydb


LOG = logging

import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.captureWarnings(True)


src = {'host':'172.20.0.3',
       'port':3306,
       'schema':'db_4',
       'user':'root',
       'passwd':'111111'}

dst = {'host':'172.20.0.3',
       'port':3306,
       'schema':'db_3',
       'user':'root',
       'passwd':'111111'}


LOG.info('copy start')



copydb.copydb(src, dst)