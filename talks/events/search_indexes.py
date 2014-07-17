from haystack import indexes

from .models import  Event


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    # text: multiple fields use to do full-text search
    text = indexes.MultiValueField(document=True, stored=False)

    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description', null=True)
    start = indexes.DateTimeField(model_attr='start', faceted=True)
    speakers = indexes.MultiValueField(faceted=True, null=True)
    departments = indexes.CharField(faceted=True, null=True)
    locations = indexes.CharField(faceted=True, null=True)
    tags = indexes.MultiValueField(faceted=True, null=True)

    # suggestions: used for spellchecking
    suggestions = indexes.SuggestionField()

    def get_model(self):
        return Event

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        #return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
        return self.get_model().objects.all()

    def prepare_suggestions(self, obj):
        suggest = []
        suggest.append(obj.title)
        if obj.description:
            suggest.append(obj.description)
        suggest.extend([tag.tag.name for tag in obj.tags.all()])
        suggest.extend([speaker.name for speaker in obj.speakers.all()])
        return suggest

    def prepare_speakers(self, obj):
        return [speaker.name for speaker in obj.speakers.all()]

    def prepare_departments(self, obj):
        if obj.department_organiser:
            return obj.department_organiser.name
        else:
            return None

    def prepare_locations(self, obj):
        if obj.location:
            return obj.location.name
        else:
            return None

    def prepare_tags(self, obj):
        return [tag.tag.name for tag in obj.tags.all()]

    def prepare_text(self, obj):
        text = []
        text.append(obj.title)
        text.append(obj.description)
        for speaker in obj.speakers.all():
            text.append(speaker.name)
        for topicitem in object.topics.all():
            text.append(topicitem.topic.name)
        return text