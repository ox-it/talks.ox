import urllib

from django import forms

DEFAULT_DATE_FORMATS = ["%d/%m/%Y"]
DEFAULT_TIME_FORMATS = ["%H:%M"]


class RevisionsFilteringForm(forms.Form):
    from_date = forms.SplitDateTimeField(label="From",
                                         required=False,
                                         input_date_formats=DEFAULT_DATE_FORMATS,
                                         input_time_formats=DEFAULT_TIME_FORMATS)
    to_date = forms.SplitDateTimeField(label="To",
                                       required=False,
                                       input_date_formats=DEFAULT_DATE_FORMATS,
                                       input_time_formats=DEFAULT_TIME_FORMATS)

    def as_url_args(self):
        return urllib.urlencode(self.data)
