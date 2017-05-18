import functools
import sys
import routes
import copy

from simpleutil.log import log

from simpleservice.wsgi import router
from simpleservice.plugin import CORE_ROUTES


LOG = log.getLogger(__name__)


def fail_gracefully(f):
    """Logs exceptions and aborts."""
    @functools.wraps(f)
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception as e:
            LOG.debug(e, exc_info=True)
            # exception message is printed to all logs
            LOG.critical(e)
            sys.exit(1)
    return wrapper


def app_factory(project_routers=None):
    @fail_gracefully
    def wrapper_factory(global_conf, **local_conf):
        mapper = routes.Mapper()
        sub_routers = []
        # NOTE(dstanek): Routers should be ordered by their frequency of use in
        # a live system. This is due to the routes implementation. The most
        # frequently used routers should appear first.
        all_api_routers = copy.copy(CORE_ROUTES)
        if project_routers:
            all_api_routers.extend(project_routers)
        all_api_routers = set(all_api_routers)
        for api_routers in all_api_routers:
            api_routers.Routers().append_routers(mapper, sub_routers)
        return router.ComposingRouter(mapper, sub_routers)
    return wrapper_factory