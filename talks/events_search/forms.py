"""
Custom search form to include the dynamic date faceting
"""

from __future__ import absolute_import
from haystack.forms import FacetedSearchForm


class DateFacetedSearchForm(FacetedSearchForm):
    def __init__(self, *args, **kwargs):
        self.filtered_date = kwargs.pop("filtered_date", None)
        super(DateFacetedSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        from .conf import URL_TO_SOLR

        sqs = super(DateFacetedSearchForm, self).search()

        if self.filtered_date:
            solr_query = URL_TO_SOLR.get(self.filtered_date, None)
            if solr_query:
                sqs = sqs.narrow(u'%s:%s' % ('start', solr_query))

        return sqs
