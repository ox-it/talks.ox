from django import forms
from django.utils.safestring import mark_safe


class BootstrappedDateTimeWidget(forms.DateTimeInput):
    def render(self, name, value, attrs=None):
        html = super(BootstrappedDateTimeWidget, self).render(name, value, attrs)
        html = """<div class="input-group date js-datetimepicker" id='""" + name + """'>
                <span class="input-group-addon">
                    <span class="glyphicon glyphicon-calendar"></span>
                </span>
        """ + html + "</div>"

        return mark_safe(html)


class BrowseEventsForm(forms.Form):
    #start_date = forms.CharField(label='Start Date', max_length=100)
    start_date = forms.DateTimeField(required=False, widget=BootstrappedDateTimeWidget(attrs={'readonly': True}))
    end_date = forms.DateTimeField(required=False, widget=BootstrappedDateTimeWidget(attrs={'readonly': True}))
    #start_date_better = BootstrappedDateTimeWidget(attrs={'readonly': True})
    #end_date = BootstrappedDateTimeWidget(attrs={'readonly': True})

 