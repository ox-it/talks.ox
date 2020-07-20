from __future__ import absolute_import
from __future__ import print_function
from django.db.models.query_utils import Q
import operator
from rest_framework.exceptions import ParseError
from talks.core.utils import parse_date
from talks.events.datasources import DEPARTMENT_DESCENDANT_DATA_SOURCE
from talks.events.models import ROLES_SPEAKER, Event, EventGroup
from datetime import datetime, timedelta
from functools import reduce



def events_search(parameters):
    """
    Return a list of events based on the DRF Request object
    :param parameters: QueryDict in the same structure as a request.GET object
    :return QuerySet of Event
    """
    queries = []

    from_date = parse_date(parameters.get("from"))
    if not from_date:
        from_date = parse_date(parameters.get("start_date"))
    if not from_date:
        raise ParseError(detail="'from' parameter is mandatory. Supply either 'today' or a date in form 'dd/mm/yy' or 'yyyy-mm-dd'.")
    else:
        queries.append(Q(start__gt=from_date))

    to_date = parse_date(parameters.get("to"), from_date)
    if to_date:
        queries.append(Q(start__lt=to_date+timedelta(1)))

    include_sub_departments = True
    subdepartments = parameters.get("subdepartments")
    if subdepartments and subdepartments == 'false':
        include_sub_departments = False

    # map between URL query parameters and their corresponding django ORM query
    list_parameters = {
        'speaker': lambda speakers: Q(personevent__role=ROLES_SPEAKER, personevent__person__slug__in=speakers),
        'venue': lambda venues: Q(location__in=venues),
        'organising_department': lambda depts: Q(department_organiser__in=get_all_department_ids(depts, include_sub_departments)),
        'topic': lambda topics: Q(topics__uri__in=topics),
        'series': lambda series: Q(group__slug__in=series),
        'seriesid': lambda seriesid: Q(group__id__in=seriesid)
    }

    for url_query_parameter, orm_mapping in list_parameters.items():
        value = parameters.getlist(url_query_parameter)
        if value:
            queries.append(orm_mapping(value))

    final_query = reduce(operator.and_, queries)
    events = Event.objects.filter(final_query).distinct().order_by('start')
    
    return events


def get_all_department_ids(departments, include_suborgs):
    if not include_suborgs:
        return departments

    # build a new list which includes the originals plus all descendants
    try:
        descendants_response = DEPARTMENT_DESCENDANT_DATA_SOURCE.get_object_list(departments)
    except Exception:
        print("Error retrieving sub-departments, returning departments only")
        return departments

    all_ids = []
    for result in descendants_response:
        # For each of the orgs being queried, extract the list of suborg ids, and add the original id too
        result_ids = map((lambda descendant: descendant['id']), result['descendants'])
        result_ids.append(result['id'])
        all_ids.extend(result_ids)
    return all_ids


def get_event_by_slug(slug):
    """Get an event by its slug
    :param slug: Event.slug
    :return: Event or None if slug does not exist
    """
    try:
        return Event.objects.get(slug=slug)
    except Event.DoesNotExist:
        return None


def get_eventgroup_by_slug(slug):
    """Get an eventgroup by its slug
    :param slug: EventGroup.slug
    :return: EventGroup or None if slug does not exist
    """
    try:
        return EventGroup.objects.get(slug=slug)
    except EventGroup.DoesNotExist:
        return None
