from inasafe_extras.raven.middleware import Sentry
from inasafe_extras.raven.base import Client


def sentry_filter_factory(app, global_conf, **kwargs):
    client = Client(**kwargs)
    return Sentry(app, client)
