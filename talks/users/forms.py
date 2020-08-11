from __future__ import absolute_import
from django import forms
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q

from talks.events import typeahead, datasources
from django.contrib.auth.models import User
from talks.users.models import Collection, TalksUser, TalksUserCollection, DEFAULT_COLLECTION_NAME, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_READER, COLLECTION_ROLES_OWNER
from talks.contributors.forms import XMLFriendlyTextField

class CollectionForm(forms.ModelForm):
    title = XMLFriendlyTextField(
        max_length=250,
        required=True
    )
    
    description = XMLFriendlyTextField(
        widget=forms.Textarea(attrs={'rows': 8}),
        required=False,
    )
    
    editor_set = forms.ModelMultipleChoiceField(
        queryset=TalksUser.objects.filter().distinct(),
        label="Other Editors",
        help_text="Share editing with another Talks Editor by typing in their full email address",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.TALKSUSERS_EMAIL_EXACT_DATA_SOURCE),
    )
    class Meta:
        model = Collection
        fields = ('title', 'description', 'public', 'editor_set')

        labels = {
            'public': "Make this list public?"
        }

        help_texts = {
            'title': "If you wish to make this list public please make sure the list has a distinctive title and description - e.g.: Recommended talks for 3rd Year Biology"
        }

    def save(self):
        collection = super(CollectionForm, self).save(commit=False)
        collection.save()

        # clear the list of editors and repopulate with the contents of the form
        collection.editor_set.through.objects.filter(role=COLLECTION_ROLES_EDITOR, collection=collection).delete()
        if 'editor_set' in self.cleaned_data:
            for user in self.cleaned_data['editor_set']:
                if collection.user_collection_permission(user) == 'owner':
                    pass
                else:
                    TalksUserCollection.objects.create(user=user,
                                                        collection=collection,
                                                        role=COLLECTION_ROLES_EDITOR)

        collection.save()
        return collection


    def clean(self):
        cleaned_data = self.cleaned_data
        public = cleaned_data.get('public')
        title = cleaned_data.get('title')

        collection = super(CollectionForm, self).save(commit=False) # get the collection instance without saving the form
        number_of_readers = collection.get_number_of_readers()

        # If we're making the collection public, ensure that the collection title is not 'My Collection'
        if public and (title == DEFAULT_COLLECTION_NAME):
            raise ValidationError({'title': 'Please change the title of your list to something less generic before making your list public'})

        if not public and (number_of_readers > 0):
            raise ValidationError({'public': 'Unable to revoke public status - there are already ' + str(number_of_readers) + ' readers following this list.'})
