import django
from django.contrib.auth.models import User
from robot.libraries.BuiltIn import BuiltIn

from talks.events import factories
FACTORIES = {
    'eventgroup': factories.EventGroupFactory,
    'person': factories.PersonFactory,
}

django.setup()


def _expose_instance(name, instance):
    BuiltIn().set_test_variable('${created %s}' % name, instance)


def create(model, **kwargs):
    normalize = lambda model: model.lower().replace('_', '').replace(' ', '')
    fun = FACTORIES.get(normalize(model))
    assert fun is not None, "Unknown model: %s. Known values are: %s" % (normalize(model), ",".join(map(normalize, FACTORIES)))
    instance = fun.create(**kwargs)
    _expose_instance(model, instance)
    return instance


def create_superuser(username, password):
    User.objects.create_superuser(username, '', password)
