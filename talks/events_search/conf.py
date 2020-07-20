"""
Configuration for our query set
Very specific to Solr unfortunately
"""

from __future__ import absolute_import
from collections import OrderedDict

from haystack.query import SearchQuerySet
from datetime import datetime



# Order used in the search UI for the filtering per start date
FACET_START_DATE = OrderedDict()
FACET_START_DATE['Next 7 days'] = {'solr_query': '[NOW TO NOW/DAY+7DAY]', 'url_param': 'next_7'}
FACET_START_DATE['Future talks'] = {'solr_query': '[NOW TO *]', 'url_param': 'future'}
FACET_START_DATE['Past talks'] = {'solr_query': '[* TO NOW]', 'url_param': 'past'}

# map an URL param to a solr query, used when a search is done
URL_TO_SOLR = {d['url_param']: d['solr_query'] for d in FACET_START_DATE.itervalues()}

# solr query to "user-friendly" name
SOLR_TO_NAME = {d['solr_query']: key for key, d in FACET_START_DATE.iteritems()}

today = datetime.today()

sqs = (SearchQuerySet()
       .facet('speakers', mincount=1).facet('location', mincount=1).facet('topics', mincount=1)).facet('group', mincount=1).facet('lists', mincount=1)

sqs_past = (SearchQuerySet()
            .filter(start__lt=today).order_by('-start')
            .facet('speakers', mincount=1).facet('location', mincount=1).facet('topics', mincount=1)).facet('group', mincount=1).facet('lists', mincount=1)

# add all the facet start date queries to the queryset
for v in FACET_START_DATE.itervalues():
    sqs = sqs.query_facet('start', v['solr_query'])
