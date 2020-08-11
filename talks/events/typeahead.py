from __future__ import absolute_import
import json
import logging

import requests
from django import forms
from django.utils.html import mark_safe
from django.core.cache import caches as django_caches

log = logging.getLogger(__name__)


class Typeahead(forms.TextInput):
    """
    Form widget converted to typeahead on client side.
    """
    is_multiple = False

    class Media:
        js = ('js/form-controls.js',)

    def __init__(self, source, attrs=None):
        """
        :param source: `DataSource` instance to provide suggestion data (required)
        """
        self.source = source
        if attrs is None:
            attrs = {}
        if self.is_multiple:
            attrs['multiple'] = True
        class_names = attrs.pop('class', '').split()
        class_names.append("typeahead")
        attrs['class'] = " ".join(class_names)
        attrs['data-source'] = source.typeahead_json()
        super(Typeahead, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        html = ""
        if value:
            if not self.is_multiple:
                value = [value]
            for v in value:
                hidden = forms.HiddenInput()
                a = None
                if self.source.is_local:
                    a = {'data-suggestion': json.dumps(self.source.get_object_by_id(v))}
                html += hidden.render(name, v, a)
            if not self.source.is_local:
                attrs['data-prefetch-url'] = self.source.get_prefetch_url(value)
        return mark_safe(html) + super(Typeahead, self).render(name, None, attrs)


class MultipleTypeahead(Typeahead):
    is_multiple = True

    def value_from_datadict(self, data, files, name):
        if hasattr(data, 'getlist'):
            return data.getlist(name)
        return data.get(name, None)


def get_objects_from_response(response, expression=None, as_list=False):
    """
    Return list of dicts representing json decoded objects. Supports only json response.

    :param response: `requests.Response` instance
    :param expression: javascript expression for extracting objects. `response` is assumed to be existing variable
    in scope holding value of `response` object. Note: only property accessor dot notation is supported.
    """
    if expression is None:
        expression = 'response'
    json = {'response': response.json()}
    properties = expression.split('.')
    while properties:
        prop = properties.pop(0)
        json = json[prop]

    # Convert to a list if necessary
    if not isinstance(json, list) and as_list:
        return [json]
    return json


class DataSource(object):
    """
    Represents external set of data reachable by HTTP.
    Exposes interface for use with typeahead.js and for fetching external data on the backend
    """

    def __init__(self, cache_key=None, url=None, get_prefetch_url=None, local=None, id_key=None, display_key=None,
                 response_expression=None, prefetch_response_expression=None, templates=None, as_list=False):
        """
        :param cache_key: cache name to use
        :param url: url for fetching suggestions
        :param get_prefetch_url: a callable returning an url for fetching data
        :param local: static data to be included (not implemented)
        :param id_key: property name used to identify objects
        :param display_key: property name used to label objects
        :param response_expression: javascript expression retrieving an array of objects from suggestion response
        :param prefetch_response_expression: same as `response_expression` but for prefetch response
        :param templates: dictionary of template strings to configure typeahead
        :param as_list: if true, convert a single result to a list of one
        """
        self.cache_key = cache_key
        self.url = url
        if get_prefetch_url:
            self.get_prefetch_url = get_prefetch_url
        self.display_key = display_key or 'name'
        self.id_key = id_key or 'id'
        self.templates = templates or {}
        self.response_expression = response_expression
        self.prefetch_response_expression = prefetch_response_expression or response_expression
        self.as_list = as_list

    @property
    def is_local(self):
        return not hasattr(self, 'get_prefetch_url')

    def get_object_by_id(self, id):
        """
        Get single object by id.
        """
        log.debug("get_object_by_id(%s)", id)
        objects = self._fetch_objects([id])
        return objects.get(id)

    def get_object_list(self, id_list):
        log.debug("get_object_list(%s)", id_list)
        return self._fetch_objects(id_list).values()

    def _fetch_objects(self, id_list):
        """
        Fetch multiple objects by their id, but check if they are cached first. Update cache accordingly.
        """
        id_list = list(filter(None, id_list))
        log.debug("_fetch_objects(%s)", id_list)
        objects = self.cache.get_many(id_list) if self.cache else []
        missing = set(id_list) - set(objects)
        log.debug("existing in cache: %s", objects)
        log.debug("missing from cache: %s", missing)
        if missing:
            url = self.get_prefetch_url(missing)
            log.debug("prefetch_url: %s", url)
            response = requests.get(url)
            response.raise_for_status()
            fetched = get_objects_from_response(response, self.prefetch_response_expression, self.as_list)
            log.debug("fetched from response: %s", fetched)
            log.debug("as list?: %r", self.as_list)
            mapped = {obj[self.id_key]: obj for obj in fetched if obj[self.id_key] in id_list}
            if mapped:
                if self.cache:
                    self.cache.set_many(mapped)
            objects.update(mapped)
        log.debug("returning objects: %s", objects)
        return objects

    @property
    def cache(self):
        if self.cache_key:
            return django_caches[self.cache_key]

    def typeahead_json(self):
        """
        Helper function returninng json for configuring a typeahead field. It's output is handled in form-control.js
        """
        config = {
            'valueKey': self.id_key,
        }
        if self.response_expression:
            config['responseExpression'] = self.response_expression
            config['prefetchResponseExpression'] = self.prefetch_response_expression
        if self.url:
            config['url'] = self.url
        if self.display_key:
            config['displayKey'] = self.display_key
        if self.templates:
            config['templates'] = self.templates
        return json.dumps(config)


class DjangoModelDataSource(DataSource):
    # TODO: might use view name as param to build urls
    def __init__(self, name, serializer=None, **kwargs):
        self.serializer = serializer
        super(DjangoModelDataSource, self).__init__(name, **kwargs)

    def get_object_by_id(self, id):
        model = self.serializer.Meta.model
        instance = model.objects.get(pk=id)
        return self.serializer(instance).data
