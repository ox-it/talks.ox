"""
Custom search view, includes our custom dynamic faceting
"""

from __future__ import absolute_import
from haystack.views import FacetedSearchView
from datetime import datetime

from talks.events.views import group_events, date_to_oxford_date


class StartDateFacetItem(object):
    """Represents a facet item in the view
    """

    def __init__(self, name, url_param, count):
        """
        Initiate a facet item
        :param name: "user-friendly" name for the item
        :param url_param: parameter that will be passed in the URL
        :param count: number of occurences for that item
        """
        self.name = name
        self.url_param = url_param
        self.count = count


class SearchView(FacetedSearchView):

    def __init__(self, *args, **kwargs):
        super(SearchView, self).__init__(*args, **kwargs)

    def build_form(self, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        form_kwargs['filtered_date'] = self.request.GET.get("filtered_date")

        return super(SearchView, self).build_form(form_kwargs)

    def extra_context(self):
        from .conf import FACET_START_DATE, SOLR_TO_NAME

        extra = super(SearchView, self).extra_context()

        if 'facets' in extra and 'queries' in extra['facets']:
            queries = extra['facets']['queries']
            facet_date = {}

            for key, count in queries.items():
                _, _, prep_key = key.partition('start_exact:')
                if prep_key in SOLR_TO_NAME:
                    facet_date[SOLR_TO_NAME[prep_key]] = count

            # need custom ordering
            ordered_dates = list()
            for key, values in FACET_START_DATE.items():
                if key in facet_date:
                    ordered_dates.append(StartDateFacetItem(key, values['url_param'], facet_date[key]))

            extra['facet_date'] = ordered_dates


        return extra

class SearchUpcomingView(SearchView):
    
    def extra_context(self):
        extra = super(SearchUpcomingView, self).extra_context()
        
        # Removing top results for now, as possibly unhelpful to users. Can reinstate later if desired by uncommenting these lines.
        # extra['top_results'] = self.get_results()[:5]
        
        
        # for top_event in extra['top_results']:
        #     ox_date = date_to_oxford_date(top_event.start)
        #     comps = ox_date.components
        #     date_str = comps['day_name']+ " " +str(comps['day_number'])+ " " +comps['month_long']+ " "
        #     date_str+= str(comps['year'])+ " ("+ str(comps['week']) + comps['ordinal']+ " Week, " +comps['term_long']+ " Term)"
        #     hours = datetime.strftime(top_event.start, '%I')
        #     minutes = datetime.strftime(top_event.start, ':%M')
        #     if minutes==":00":
        #         minutes = ""
        #     ampm = datetime.strftime(top_event.start, '%p')
        #     top_event.oxford_date_time = date_str +" "+ str(int(hours))+minutes+ampm.lower()

        now = datetime.now()
        extra['future_results'] = self.get_results().filter(start__gte=now).order_by('start')

        # return all top results and future_results. These will be displayed on a single page.
        
        extra['grouped_future_results'] = group_events(extra['future_results'])
        
        return extra
        
class SearchPastView(SearchView):

    def extra_context(self):
        extra = super(SearchPastView, self).extra_context()
        
        # pass all past events, grouped by date
        extra['grouped_past_results'] = group_events(self.get_results())
        
        return extra
