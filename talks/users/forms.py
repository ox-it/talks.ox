from django import forms
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q

from talks.events import typeahead, datasources
from talks.users.models import Collection, TalksUser, TalksUserCollection, DEFAULT_COLLECTION_NAME, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_READER, COLLECTION_ROLES_OWNER

class CollectionForm(forms.ModelForm):

    editor_set = forms.ModelMultipleChoiceField(
        queryset=TalksUser.objects.filter().distinct(),
        label="Other Editors",
        help_text="Share editing with another Talks Editor by typing in their full email address",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.USERS_EMAIL_EXACT_DATA_SOURCE),
    )
    class Meta:
        model = Collection
        fields = ('title', 'description', 'public', 'editor_set')

        labels = {
            'public': "Make this list public?"
        }

    def save(self):
        collection = super(CollectionForm, self).save(commit=False)
        collection.save()

        # clear the list of editors and repopulate with the contents of the form
        collection.editor_set.through.objects.filter(role=COLLECTION_ROLES_EDITOR, collection=collection).delete()
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

        # If we're making the collection public, ensure that the collection title is not 'My Collection'
        if public and (title == DEFAULT_COLLECTION_NAME):
            raise ValidationError({'title': 'Please change the title of your list to something less generic before making your list public'})
