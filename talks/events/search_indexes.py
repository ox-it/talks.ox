from haystack import indexes

from .models import  Event


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    # text: multiple fields use to do full-text search
    text = indexes.CharField(document=True, use_template=True)

    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description', null=True)
    start = indexes.DateTimeField(model_attr='start', faceted=True)
    speakers = indexes.MultiValueField(faceted=True, null=True)
    departments = indexes.CharField(faceted=True, null=True)
    locations = indexes.CharField(faceted=True, null=True)
    topics = indexes.MultiValueField(faceted=True, null=True)

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
        suggest.extend([topic.topic.name for topic in obj.topics.all()])
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

    def prepare_topics(self, obj):
        return [topic.topic.name for topic in obj.topics.all()]
