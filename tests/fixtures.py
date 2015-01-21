import django
from django.contrib.auth.models import User, Group
from robot.libraries.BuiltIn import BuiltIn

from talks.events import factories
from talks.events.models import Event, EventGroup, Person, PersonEvent, TopicItem, ROLES_SPEAKER, ROLES_HOST, ROLES_ORGANISER
from talks.users.authentication import GROUP_EDIT_EVENTS
from django.contrib.contenttypes.models import ContentType

from events import *


FACTORIES = {
    'eventgroup': factories.EventGroupFactory,
    'person': factories.PersonFactory,
    'event': factories.EventFactory,
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


def create_contributors_group():
    group = Group(name=GROUP_EDIT_EVENTS)
    group.save()
    return group


def create_test_data():
    #users
    contributors_group = create_contributors_group()
    contrib_user = User.objects.create_user('contrib_user', email='contrib.user@users.com', password='pw')
    contrib_user.groups.add(contributors_group)
    non_contrib_user = User.objects.create_user('non_contrib_user', email="non.contrib@user.com", password='pw')
    non_contrib_user.groups.add(contributors_group)
    #persons
    person1 = Person.objects.create(name="James Bond", bio="secret agent")
    person2 = Person.objects.create(name="Luke Skywalker", bio="Jedi")
    person3 = Person.objects.create(name="Darth Vader", bio="Sith")
    #event group
    event_group = factories.EventGroupFactory.create(title=group1_title,
                                                     department_organiser='oxpoints:23232627',)
    event_group.organisers.add(person1)
    event_group.organisers.add(person2)
    event_group.save()

    #event
    event = factories.EventFactory.create(title=event1_title, slug=event1_slug,
                                          description='Description for a talk about maths',
                                          location='oxpoints:40002001',
                                          department_organiser='oxpoints:23233906')
    event.editor_set.add(contrib_user)
    PersonEvent.objects.create(person=person1, event=event, role=ROLES_SPEAKER)
    PersonEvent.objects.create(person=person2, event=event, role=ROLES_ORGANISER)
    PersonEvent.objects.create(person=person3, event=event, role=ROLES_HOST)
    event_ct = ContentType.objects.get_for_model(Event)
    TopicItem.objects.create(uri="http://id.worldcat.org/fast/1429860",     # Biodiversity
                             content_type=event_ct,
                             object_id=event.id)
    TopicItem.objects.create(uri="http://id.worldcat.org/fast/1737875",     # Aquatic biodiversity
                             content_type=event_ct,
                             object_id=event.id)
    event.save()

    event2 = factories.EventFactory(title=event2_title,
                                    slug=event2_slug,
                                    description=event2_description,
                                    location=event2_location)
    event2.save()
    PersonEvent.objects.create(person=person2, event=event2, role=ROLES_ORGANISER)

