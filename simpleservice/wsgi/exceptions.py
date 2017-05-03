class ConfigNotFound(Exception):
    def __init__(self, path):
        msg = 'Could not find config at %(path)s' % {'path': path}
        super(ConfigNotFound, self).__init__(msg)


class PasteAppNotFound(Exception):
    def __init__(self, name, path):
        msg = ("Could not load paste app '%(name)s' from %(path)s" %
               {'name': name, 'path': path})
        super(PasteAppNotFound, self).__init__(msg)
