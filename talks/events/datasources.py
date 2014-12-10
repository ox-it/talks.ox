from urllib import urlencode

from django.conf import settings

from talks.api import serializers
from talks.events import typeahead


class OxPointDataSource(typeahead.DataSource):
    def __init__(self, **kwargs):
        _types = kwargs.pop('types', [])
        url = settings.API_OX_PLACES_URL + "suggest?" + urlencode({'type_exact': _types}, doseq=True) + '&q=%QUERY'
        super(OxPointDataSource, self).__init__(
            'oxpoints',
            url=url,
            response_expression='response._embedded.pois',
            # XXX: forcing api to return list if requesting single object
            get_prefetch_url=lambda values: settings.API_OX_PLACES_URL + ",".join(values) + ","
        )

LOCATION_DATA_SOURCE = OxPointDataSource(
    types=['/university/building', '/university/site', '/leisure/museum', '/university/college', '/university/library']
)
DEPARTMENT_DATA_SOURCE = OxPointDataSource(
    types=['/university/department', '/university/museum', '/university/college', '/university/hall',
           '/university/division']
)
TOPICS_DATA_SOURCE = typeahead.DataSource(
    'topics',
    url=settings.TOPICS_URL + "suggest?count=10&q=%QUERY",
    get_prefetch_url=lambda values: ("%sget?%s" % (settings.TOPICS_URL, urlencode({'uri': values}, doseq=True))),
    display_key='prefLabel',
    id_key='uri',
    response_expression='response._embedded.concepts',
)
PERSONS_DATA_SOURCE = typeahead.DjangoModelDataSource(
    'speakers',
    url='/talks/persons/suggest?q=%QUERY',
    display_key='title',
    serializer=serializers.PersonSerializer,
    id_key='slug',
)
USERS_DATA_SOURCE = typeahead.DjangoModelDataSource(
    'users',
    url='/api/user/suggest?q=%QUERY',
    display_key='email',
    serializer=serializers.UserSerializer
)
