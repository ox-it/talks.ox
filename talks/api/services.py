from django.db.models.query_utils import Q
import operator
from rest_framework.exceptions import ParseError
from talks.core.utils import parse_date
from talks.events.models import ROLES_SPEAKER, Event


def events_search(request):
    """
    Return a list of events based on the DRF Request object
    :param request: Django Rest Framework Request object
    :return QuerySet of Event
    """
    queries = []

    from_date = parse_date(request.GET.get("from"))
    if not from_date:
        raise ParseError(detail="'from' parameter is mandatory. Supply either 'today' or a date in form 'dd/mm/yy'.")
    else:
        queries.append(Q(start__gt=from_date))

    to_date = parse_date(request.GET.get("to"))
    if to_date:
        queries.append(Q(start__lt=to_date))

    # map between URL query parameters and their corresponding django ORM query
    list_parameters = {
        'speaker': lambda speakers: Q(personevent__role=ROLES_SPEAKER, personevent__person__slug__in=speakers),
        'venue': lambda venues: Q(location__in=venues),
        'organising_department': lambda depts: Q(department_organiser__in=depts),
        'topic': lambda topics: Q(topics__uri__in=topics)
    }

    for url_query_parameter, orm_mapping in list_parameters.iteritems():
        value = request.GET.getlist(url_query_parameter)
        if value:
            queries.append(orm_mapping(value))

    final_query = reduce(operator.and_, queries)
    events = Event.published.filter(final_query).distinct().order_by('start')

    return events
