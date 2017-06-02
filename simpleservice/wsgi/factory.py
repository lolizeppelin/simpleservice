import functools
import sys
import routes

from simpleutil.log import log as logging

from simpleservice.wsgi import router


LOG = logging.getLogger(__name__)


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
        if project_routers:
            all_api_routers = set(project_routers)
            for api_routers in all_api_routers:
                api_routers.Routers().append_routers(mapper, sub_routers)
        return router.ComposingRouter(mapper, sub_routers)
    return wrapper_factory
