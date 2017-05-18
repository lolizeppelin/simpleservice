from simpleutil.log import log as logging
from simpleservice.ormdb.api import MysqlDriver

LOG = logging.getLogger(__name__)

DbDriver = None


def init_session(name, conf):
    if DbDriver is None:
        mysql_driver = MysqlDriver(name, conf)
        mysql_driver.start()
        global DbDriver
        DbDriver = mysql_driver
    else:
        LOG.warning("Do not call init_session more then once")


def get_session(readonly=False):
    if DbDriver is None:
        raise RuntimeError('Database not connected')
    if readonly:
        return DbDriver.rsession()
    return DbDriver.session()
