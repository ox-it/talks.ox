from django import template
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
register = template.Library()


@register.simple_tag(takes_context=True)
def facet_param(context, key, value):
    request = context['request']
    query_string = request.META['QUERY_STRING']
    return _set_parameter(query_string, key, value)


@register.simple_tag(takes_context=True)
def facet_single_param(context, *args, **kwargs):
    request = context['request']
    query_string = request.META['QUERY_STRING']
    return _update_parameter(query_string, **kwargs)


@register.simple_tag(takes_context=True)
def facet_remove_all(context, *args):
    """
    Clean a query string from all instances
    of one key
    """
    request = context['request']
    query_string = request.META['QUERY_STRING']
    return _remove_all_parameter(query_string, *args)


@register.simple_tag(takes_context=True)
def facet_selected(context, **kwargs):
    """
    Returns the return_value as specified only if the key/value
    is present in the query string.
    """
    already_there = False
    request = context['request']
    query_string = request.META['QUERY_STRING']
    for k, v in kwargs.items():
        if _parameter_present(query_string, k, v):
            return kwargs.get('return_value', "filter-selected")
    return ""

@register.filter()
def can_edit(user, event):
    return event.user_can_edit(user)

def _set_parameter(query_string, key, value):
    """
    Add a parameter to a query string if it's not there,
    Remove the parameter if it was already there
    """
    parameters = []
    already_there = False
    if query_string:
        for p in query_string.split('&'):
            k, v = p.split('=')
            if str(k) == str(key) and str(v) == str(value):
                already_there = True
            else:
                parameters.append('{0}={1}'.format(k, v))
    if not already_there:
        parameters.append('{0}={1}'.format(key, value))
    return '?%s' % '&'.join(parameters)


def _update_parameter(query_string, **kwargs):
    """
    Returns the query string with the key updated (if already present in query string
    to the value given as a parameter
    """
    parameters = {}
    if query_string:
        for p in query_string.split('&'):
            k, v = p.split('=')
            parameters[k] = v
    for k, v in kwargs.items():
        parameters[k] = v
    return '?%s' % '&'.join(['{0}={1}'.format(k, v) for (k,v) in parameters.items()])


def _remove_all_parameter(query_string, *args):
    """
    Removes all occurrences of a key (or a list of keys, separated by a comma) and its values
    """
    parameters = []
    if query_string:
        for p in query_string.split('&'):
            k, v = p.split('=')
            if k not in args:
                parameters.append('{0}={1}'.format(k, v))
    return '?%s' % '&'.join(parameters)


def _parameter_present(query_string, key, value):
    already_there = False
    if query_string:
        for p in query_string.split('&'):
            k, v = p.split('=')
            if str(k) == str(key) and str(v) == str(value):
                already_there = True
    return already_there
