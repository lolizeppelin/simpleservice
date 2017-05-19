from simpleutil.config import cfg

from simpleutil.log import log as logging
from simpleservice.ormdb.config import database_opts
from simpleservice.ormdb.api import MysqlDriver

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

DbDriver = None

manager_group = cfg.OptGroup(name='manager', title='Manager options')
CONF.register_group(manager_group)

def init_session():
    global DbDriver
    if DbDriver is None:
        LOG.info("Try connect database for manager")
        CONF.register_opts(database_opts, manager_group)
        mysql_driver = MysqlDriver(manager_group.name,
                                   CONF[manager_group.name])
        mysql_driver.start()
        DbDriver = mysql_driver
    else:
        LOG.warning("Do not call init_session more then once")


def get_session(readonly=False):
    global DbDriver
    if DbDriver is None:
        init_session()
        # raise RuntimeError('Database not connected')
    if readonly:
        return DbDriver.rsession
    return DbDriver.session
