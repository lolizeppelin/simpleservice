import os
from simpleservice.ormdb.tools import sqldecode

disktop = r'C:\Users\loliz_000\Desktop'

analyze = sqldecode.MysqlAnalyze(os.path.join(disktop, 'target.sql'))

analyze()

analyze.printing()
