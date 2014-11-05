import json

from django import forms
from django.utils.html import mark_safe


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

    def render(self, name, value, attrs=None):
        html = ""
        if value:
            if not self.is_multiple:
                value = [value]
            for v in value:
                hidden = forms.HiddenInput()
                a = None
                if self.source.get_data_by_id:
                    a = {'data-suggestion': json.dumps(self.source.get_data_by_id(v))}
                html += hidden.render(name, v, a)
            if self.source.get_prefetch_url:
                attrs['data-prefetch-url'] = self.source.get_prefetch_url(value)
        return mark_safe(html) + super(Typeahead, self).render(name, None, attrs)


class MultipleTypeahead(Typeahead):
    is_multiple = True

    def value_from_datadict(self, data, files, name):
        if hasattr(data, 'getlist'):
            return data.getlist(name)
        return data.get(name, None)


class DataSource(object):
    """
    Represents external set of data reachable by HTTP.
    Exposes interface for use with typeahead.js and for fetching external data on the backend
    """

    def __init__(self, url=None, get_prefetch_url=None, local=None, id_key=None, display_key=None,
                 response_expression=None, prefetch_response_expression=None, templates=None, get_data_by_id=None):
        """
        :param url: url for fetching suggestions
        :param get_prefetch_url: a callable returning an url for fetching data
        :param local: static data to be included (not implemented)
        :param id_key: property name used to identify objects
        :param display_key: property name used to label objects
        :param response_expression: javascript expression retrieving an array of objects from suggestion response
        :param prefetch_response_expression: same as `response_expression` but for prefetch response
        :param templates: dictionary of template strings to configure typeahead
        :param get_data_by_id: a callable fetching object given an id
        """
        self.url = url
        self.get_prefetch_url = get_prefetch_url
        self.display_key = display_key or 'name'
        self.id_key = id_key or 'id'
        self.templates = templates or {}
        self.response_expression = response_expression
        self.prefetch_response_expression = prefetch_response_expression or response_expression
        self.get_data_by_id = get_data_by_id

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


class DjangoInternalDataSource(DataSource):
    def __init__(self, name, view):
        self._view = view
        super(DjangoInternalDataSource, self).__init__(name, None)

    @property
    def url(self):
        from django.core.urlresolvers import reverse
        return reverse(self.view)
