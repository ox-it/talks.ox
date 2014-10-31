from datetime import date
import urllib

from django import forms
from django.forms.extras.widgets import SelectDateWidget


DATE_CHOICES = range(2014, date.today().year + 1)


class RevisionsFilteringForm(forms.Form):
    from_date = forms.DateTimeField(widget=SelectDateWidget(years=DATE_CHOICES),
                                    label="From",
                                    required=False)
    to_date = forms.DateTimeField(widget=SelectDateWidget(years=DATE_CHOICES),
                                  label="To",
                                  required=False)

    def as_url_args(self):
        return urllib.urlencode(self.data)