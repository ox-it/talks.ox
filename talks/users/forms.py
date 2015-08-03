from django import forms
from django.db.models.query_utils import Q

from talks.events import typeahead, datasources
from talks.users.models import Collection, TalksUser, TalksUserCollection, COLLECTION_ROLES_EDITOR, COLLECTION_ROLES_READER, COLLECTION_ROLES_OWNER

class CollectionForm(forms.ModelForm):

    editor_set = forms.ModelMultipleChoiceField(
        queryset=TalksUser.objects.filter().distinct(),
        label="Other Editors",
        help_text="Share editing with another Talks Editor by typing in their email address",
        required=False,
        widget=typeahead.MultipleTypeahead(datasources.USERS_DATA_SOURCE),
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

