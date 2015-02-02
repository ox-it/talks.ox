import mock

from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from talks.events import factories, models
from talks.events.models import EVENT_PUBLISHED, PersonEvent, ROLES_SPEAKER

FUTURE_DATE_STRING = "2018-01-01 19:00"
PAST_DATE_STRING = "2011-01-01 20:00"

TOPIC_1429860_MOCK_RESPONSE = {"_links":{"self":{"href":"/search?uri=http://id.worldcat.org/fast/1429860"}},"_embedded":{"concepts":[{"uri":"http://id.worldcat.org/fast/1429860","prefLabel":"Biodiversity","altLabels":["Biotic diversity","Diversification, Biological","Diversity, Biotic","Biological diversity","Diversity, Biological","Biological diversification"],"related":[{"label":"Biology","uri":"http://id.worldcat.org/fast/832383"},{"label":"Ecological heterogeneity","uri":"http://id.worldcat.org/fast/901453"}]}]}}


class TestAPI(TestCase):

    def setUp(self):
        self.event1_slug = "future-event"
        self.group1_slug = "talks-conference"
        self.speaker1_slug = "james-bond"
        self.location1 = "oxpoints:40002001"
        self.department1 = "oxpoints:23232503"
        self.topic1_uri = "http://id.worldcat.org/fast/1429860"
        # create some sample events and series
        person1 = factories.PersonFactory.create(
            name="James Bond",
            bio="Secret Agent",
            slug=self.speaker1_slug,
        )
        person2 = factories.PersonFactory.create(
            name="Doctor Evil",
            bio="Super Villain",
        )
        group1 = factories.EventGroupFactory.create(
            title="talks conference",
            slug=self.group1_slug,
            description="a conference",
            group_type='Conference',
        )
        group2 = factories.EventGroupFactory.create(
            title="talks seminar",
            slug="talks-seminar",
            description="a seminar",
            group_type='Seminar Series'
        )
        future_event = factories.EventFactory.create(
            title="A future event",
            slug=self.event1_slug,
            description="the first sample event",
            start=FUTURE_DATE_STRING,
            end=FUTURE_DATE_STRING,
            status=EVENT_PUBLISHED,
            location=self.location1,
            department_organiser=self.department1,
            group=group1,
        )
        past_event = factories.EventFactory.create(
            title="A past event",
            slug="past-event",
            description="the second sample event",
            start=PAST_DATE_STRING,
            end=PAST_DATE_STRING,
            status=EVENT_PUBLISHED,
            group=group1,
        )
        factories.PersonEventFactory.create(
            person=person1,
            event=future_event,
            role=ROLES_SPEAKER,
        )
        factories.PersonEventFactory.create(
            person=person2,
            event=past_event,
            role=ROLES_SPEAKER,
        )
        ct = ContentType.objects.get_for_model(models.Event)
        print ct
        ti = factories.TopicItemFactory_noSubFactory.create(
            uri=self.topic1_uri,
            content_type=ct,
            object_id=future_event.id,
        )
        # ti = models.TopicItem.objects.get_or_create(uri=self.topic1_uri,
        #                                             content_type=ct,
        #                                             object_id=future_event.id)
        ti.save()
        future_event.save()
        self.req_factory = APIRequestFactory()
        self.client = APIClient()

    @mock.patch('requests.get', autospec=True)
    def test_retrieve_event_happy(self, requests_get):
        requests_get.return_value.json.return_value = TOPIC_1429860_MOCK_RESPONSE
        response = self.client.get('/api/talks/' + self.event1_slug)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")

    def test_retrieve_event_404(self):
        response = self.client.get('/api/talks/foo')
        self.assertEquals(response.status_code, 404)

    @mock.patch('requests.get', autospec=True)
    def test_retrieve_series_happy(self, requests_get):
        requests_get.return_value.json.return_value = TOPIC_1429860_MOCK_RESPONSE
        response = self.client.get('/api/series/' + self.group1_slug)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "talks conference")
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")

    def test_retrieve_series_invalid(self):
        response = self.client.get('/api/series/foo/')
        self.assertEquals(response.status_code, 404)

    def test_search_no_results(self):
        # ensure _links section still exists
        # ensure _embedded section still exists with empty talks field
        response = self.client.get('/api/talks/search?from=01/01/15&to=02/01/15')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")

    @mock.patch('requests.get', autospec=True)
    def test_search_from_to(self, requests_get):
        #test the from and to search fields
        #expect only the future search
        requests_get.return_value.json.return_value = TOPIC_1429860_MOCK_RESPONSE
        response = self.client.get('/api/talks/search?from=01/01/15&to=01/01/20')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")
        #expect 2 results for this search
        response = self.client.get('/api/talks/search?from=01/01/01')
        self.assertContains(response, "title", 2)

    @mock.patch('requests.get', autospec=True)
    def test_search_speaker(self, requests_get):
        requests_get.return_value.json.return_value = TOPIC_1429860_MOCK_RESPONSE
        response = self.client.get('/api/talks/search?from=01/01/01&speaker=' + self.speaker1_slug )
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")

        # Note = currently failing since we don't yet embed speakers in event response
        self.assertContains(response, "James Bond")
        self.assertContains(response, "A future event")

    @mock.patch('requests.get', autospec=True)
    def test_search_venue(self, requests_get):
        requests_get.return_value.json.return_value = TOPIC_1429860_MOCK_RESPONSE
        response = self.client.get('/api/talks/search?from=01/01/01&venue=' + self.location1)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        # TODO expose venue in response, will need further mockup
        #self.assertContains(response, "Banbury Road")

    @mock.patch('requests.get', autospec=True)
    def test_search_organising_department(self, requests_get):
        requests_get.return_value.json.return_value = TOPIC_1429860_MOCK_RESPONSE
        response = self.client.get('/api/talks/search?from=01/01/01&organising_department=' + self.department1)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        # TODO expose dept in response, will need further mockup
        #self.assertContains(response, "Chemical Biology")

    @mock.patch('requests.get', autospec=True)
    def test_search_topic(self, requests_get):
        requests_get.return_value.json.return_value = TOPIC_1429860_MOCK_RESPONSE
        response = self.client.get('/api/talks/search?from=01/01/01&topic=' + self.topic1_uri)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "Biodiversity")
