from haystack import indexes

from .models import Event
from talks.events.models import EVENT_IN_PREPARATION, EVENT_PUBLISHED


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    # text: multiple fields use to do full-text search
    text = indexes.MultiValueField(document=True, stored=False)

    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description', null=True)
    start = indexes.DateTimeField(model_attr='start', faceted=True)
    speakers = indexes.MultiValueField(faceted=True, null=True)
    department = indexes.CharField(faceted=True, null=True)
    location = indexes.CharField(faceted=True, null=True)
    topics = indexes.MultiValueField(faceted=True, null=True)
    published = indexes.BooleanField(null=False)

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
        if obj.title:
            suggest.append(obj.title)
        if obj.description:
            suggest.append(obj.description)
        topics = obj.api_topics
        if topics:
            suggest.extend([topic.prefLabel for topic in topics])
        suggest.extend([speaker.name for speaker in obj.speakers.all()])
        return suggest

    def prepare_speakers(self, obj):
        return [speaker.name for speaker in obj.speakers.all()]

    def prepare_department(self, obj):
        if obj.department_organiser:
            api_dept = obj.api_organisation
            if api_dept:
                return api_dept.name
        return None

    def prepare_location(self, obj):
        if obj.location:
            api_loc = obj.api_location
            if api_loc:
                return api_loc.name
        return None

    def prepare_topics(self, obj):
        topics = obj.api_topics
        if topics:
            return [topic.prefLabel for topic in topics]
        else:
            return None

    def prepare_text(self, obj):
        text = []
        text.append(obj.title)
        text.append(obj.description)
        for speaker in obj.speakers.all():
            text.append(speaker.name)
        topics = obj.api_topics
        if topics:
            text.extend([topic.prefLabel for topic in topics])
        return text

    def prepare_published(self, obj):
        if obj.embargo:
            return False
        elif obj.status == EVENT_IN_PREPARATION:
            return False
        elif obj.status == EVENT_PUBLISHED:
            return True
        else:
            return False
