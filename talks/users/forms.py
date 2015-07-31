from django import forms

from talks.users.models import Collection

class CollectionForm(forms.ModelForm):

    class Meta:
        fields = ('title', 'description', 'public')
        model = Collection

        labels = {
            'public': "Make this list public?"
        }
