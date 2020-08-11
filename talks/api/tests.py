from __future__ import absolute_import
import mock

from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from talks.events import factories, models
from talks.users import models
from talks.events.models import EVENT_PUBLISHED, PersonEvent, ROLES_SPEAKER
from django.conf import settings
import datetime

FUTURE_DATE_STRING = (datetime.datetime.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d %I:%M")
FUTURE_STRING = datetime.datetime.strptime(FUTURE_DATE_STRING, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")

PAST_DATE_STRING = "2011-01-01 20:00"
PAST_STRING = datetime.datetime.strptime(PAST_DATE_STRING, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")

TODAY_DATE_STRING = datetime.date.today().strftime("%Y-%m-%d %I:%M")
TODAY_STRING = datetime.date.today().strftime("%Y-%m-%d")

TOPIC_1429860_MOCK_RESPONSE = {"_links":{"self":{"href":"/search?uri=http://id.worldcat.org/fast/1429860"}},"_embedded":{"concepts":[{"uri":"http://id.worldcat.org/fast/1429860","prefLabel":"Biodiversity","altLabels":["Biotic diversity","Diversification, Biological","Diversity, Biotic","Biological diversity","Diversity, Biological","Biological diversification"],"related":[{"label":"Biology","uri":"http://id.worldcat.org/fast/832383"},{"label":"Ecological heterogeneity","uri":"http://id.worldcat.org/fast/901453"}]}]}}
LOC_40002001_MOCK_RESPONSE = {"_embedded": {"pois": [{"_embedded": {"files": [{"location": "oxpoints/40002001/depiction/original/primary.jpg","primary": True,"type": "depiction","url": "//mox-static-files.oucs.ox.ac.uk/oxpoints/40002001/depiction/original/primary.jpg"},{"location": "oxpoints/40002001/depiction/original/primary.jpg","type": "depiction","url": "//mox-static-files.oucs.ox.ac.uk/oxpoints/40002001/depiction/original/primary.jpg"}]},"_links": {"child": [{"href": "/places/oxpoints:23233603"},{"href": "/places/oxpoints:23233671","title": "11-13 Banbury Road","type": ["/university/building"],"type_name": ["Building"]},{"href": "/places/oxpoints:23233670","title": "7-9 Banbury Road","type": ["/university/building"],"type_name": ["Building"]},{"href": "/places/oxpoints:23233669","title": "15-19 Banbury Road","type": ["/university/building"],"type_name": ["Building"]}],"parent": {"href": "/places/oxpoints:31337175","title": "IT Services","type": ["/university/department"],"type_name": ["Department"]},"self": {"href": "/places/oxpoints:40002001"}},"address": "7-19 Banbury Road OX2 6NN","alternative_names": ["IT Services, Banbury Road"],"distance": 0,"id": "oxpoints:40002001","identifiers": ["osm:99933769-way","oxpoints:40002001"],"lat": "51.76001","lon": "-1.26035","name": "7-19 Banbury Road","name_sort": "7-19 Banbury Road","shape": "POLYGON ((-1.2604547 51.7597247,-1.2604524 51.759703600000002,-1.2606225 51.759693400000003,-1.2606263 51.759717899999998,-1.2606718 51.759715200000002,-1.2606742 51.759729900000004,-1.260875 51.759717299999998,-1.2609002 51.759870900000003,-1.2609514 51.7598677,-1.2609628 51.759937299999997,-1.2609819 51.759936099999997,-1.2610376 51.760275399999998,-1.2606854 51.760297899999998,-1.260475 51.760310799999999,-1.2604334 51.7600865,-1.2605216 51.760081800000002,-1.2605182 51.760061299999997,-1.2605157 51.760043799999998,-1.2604056 51.760051799999999,-1.2603867 51.759929399999997,-1.2604979 51.759923100000002,-1.2604921 51.7598805,-1.2604867 51.759852799999997,-1.2603628 51.759858199999996,-1.2603454 51.759729800000002,-1.2604547 51.7597247))","type": ["/university/site"],"type_name": ["Site"]}]},"_links": {"self": {"href": "/places/oxpoints:40002001%2C"}},"count": 1}
DEP_23232503_MOCK_RESPONSE = {"_embedded": {"pois": [{"_links": {"child": [{"href": "/places/oxpoints:23232548"}],"parent": {"href": "/places/oxpoints:23232546","title": "Department of Chemistry","type": ["/university/department"],"type_name": ["Department"]},"primary_place": {"href": "/places/oxpoints:23232548"},"self": {"href": "/places/oxpoints:23232503"}},"address": "off South Parks Road OX1 3TA","alternative_names": ["Bayley Group"],"distance": 0,"id": "oxpoints:23232503","identifiers": ["oxpoints:23232503","finance:DQ"],"lat": "51.757797","lon": "-1.253332","name": "Chemical Biology","name_sort": "Chemical Biology","shape": "POLYGON ((-1.252908 51.758493199999997 0,-1.2525447 51.758077800000002 0,-1.252753 51.758007999999997 0,-1.2527069 51.757955299999999 0,-1.2532898 51.757759999999998 0,-1.2533847 51.7578685 0,-1.2532655 51.757908399999998 0,-1.2532846 51.757930299999998 0,-1.2533138 51.757963699999998 0,-1.2533718 51.757944299999998 0,-1.253638 51.758248700000003 0,-1.252908 51.758493199999997 0))","social_twitter": ["https://www.twitter.com/bayley_lab"],"type": ["/university/department"],"type_name": ["Department"],"website": "http://bayley.chem.ox.ac.uk/"}]},"_links": {"self": {"href": "/places/oxpoints:23232503%2C"}},"count": 1}
DEP_23232546_SUBORGS_MOCK_RESPONSE = {"descendants": [{"id": "oxpoints:23232604","title": "Inorganic Chemistry Laboratory"},{"id": "oxpoints:51830315","title": "Theory and Modelling in Chemical Sciences CDT"},{"id": "oxpoints:52835523","title": "Chemistry Research Laboratory"},{"id": "oxpoints:23232687","title": "Physical and Theoretical Chemistry Laboratory"},{"id": "oxpoints:58224544","title": "Organic Chemistry"},{"id": "oxpoints:23232503","title": "Chemical Biology"},{"id": "oxpoints:23232843","title": "Synthesis for Biology and Medicine CDT"}],"id": "oxpoints:23232546"}

MOCK_URL_RESPONSES = {
    settings.API_OX_PLACES_URL + 'oxpoints:40002001,': LOC_40002001_MOCK_RESPONSE,
    settings.API_OX_PLACES_URL + 'oxpoints:23232503,': DEP_23232503_MOCK_RESPONSE,
    settings.API_OX_PLACES_URL + 'oxpoints:23232546/organisation-descendants': DEP_23232546_SUBORGS_MOCK_RESPONSE,
    settings.TOPICS_URL + 'get?uri=http%3A%2F%2Fid.worldcat.org%2Ffast%2F1429860': TOPIC_1429860_MOCK_RESPONSE,
    }

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            return

    url = args[0]
    response_content = MOCK_URL_RESPONSES.get(url, "Couldn't get mock response for url %s"%url)
    return MockResponse(response_content, 200)


def mock_get(url):
    return MOCK_URL_RESPONSES[url]


class TestAPI(TestCase):

    def setUp(self):
        self.event1_slug = "future-event"
        self.group1_slug = "talks-conference"
        self.collection1_slug = "it-collection"
        self.speaker1_slug = "james-bond"
        self.location1 = "oxpoints:40002001"
        self.location_details1 = "First floor"
        self.department1 = "oxpoints:23232503"  # Chemical Biology
        self.super_department = "oxpoints:23232546"  # Department of Chemistry
        self.topic1_uri = "http://id.worldcat.org/fast/1429860"
        # create some sample events, series and collections
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
        collection1 = factories.EventCollectionFactory.create(
            title="IT talks collection",
            slug=self.collection1_slug,
            description="a collection of IT talks",
            public=True,
        )
        collection2 = factories.EventCollectionFactory.create(
            title="My second collection",
            slug="my-second-collection",
            description="second collection",
        )
        future_event = factories.EventFactory.create(
            title="A future event",
            slug=self.event1_slug,
            description="the first sample event",
            start=FUTURE_DATE_STRING,
            end=FUTURE_DATE_STRING,
            status=EVENT_PUBLISHED,
            location=self.location1,
            location_details=self.location_details1,
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

        today_event = factories.EventFactory.create(
            title="A today event",
            slug="today-event",
            description="a today event event",
            start=TODAY_DATE_STRING,
            end=TODAY_DATE_STRING,
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
        ti = factories.TopicItemFactory_noSubFactory.create(
            uri=self.topic1_uri,
            content_type=ct,
            object_id=future_event.id,
        )
        ti.save()
        future_event.save()

        collectedItemCt = ContentType.objects.get_for_model(models.CollectedDepartment)
        collectedDep = factories.CollectedDepartmentFactory.create(
            department=self.department1
        )
        collectionItem = factories.CollectionItemFactory.create(
            collection=collection1,
            content_type=collectedItemCt,
            object_id=collectedDep.id
        )
        self.req_factory = APIRequestFactory()
        self.client = APIClient()

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_retrieve_event_happy(self, requests_get):
        response = self.client.get('/api/talks/' + self.event1_slug)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")
        self.assertContains(response, "James Bond")
        self.assertContains(response, "First floor")

    def test_retrieve_event_404(self):
        response = self.client.get('/api/talks/foo')
        self.assertEquals(response.status_code, 404)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_retrieve_series_happy(self, requests_get):
        response = self.client.get('/api/series/' + self.group1_slug)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "talks conference")
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")

    def test_retrieve_series_invalid(self):
        response = self.client.get('/api/series/foo/')
        self.assertEquals(response.status_code, 404)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_retrieve_collection_happy(self, requests_get):
        response = self.client.get('/api/collections/id/' + self.collection1_slug)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "IT talks collection")
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        # should return a talk organised by department 1
        self.assertContains(response, "A future event")
        self.assertNotContains(response, "A past event")

    def test_retrieve_collection_invalid(self):
        response = self.client.get('/api/collections/id/foo')
        self.assertEquals(response.status_code, 404)

    def test_search_no_results(self):
        # ensure _links section still exists
        # ensure _embedded section still exists with empty talks field
        response = self.client.get('/api/talks/search?from=01/01/15&to=02/01/15')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_from_today(self, requests_get):
        #test the from=today search
        #expect only the future search
        response = self.client.get('/api/talks/search?from='+ TODAY_STRING)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")
        self.assertContains(response, "A today event")
        self.assertNotContains(response, "A past event")

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_edge_dates(self, requests_get):
        #test the from past_event_date,  to future_event_date search
        #expect all the events in the results
        response = self.client.get('/api/talks/search?from='+ PAST_STRING +'&to=' + FUTURE_STRING)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")
        self.assertContains(response, "A today event")
        self.assertContains(response, "A past event")

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_from_to(self, requests_get):
        #test the from and to search fields
        #expect only the future search
        response = self.client.get('/api/talks/search?from=01/01/15&to=01/01/30')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "A future event")
        #expect 2 results for this search
        response = self.client.get('/api/talks/search?from=01/01/01')
        # self.assertContains(response, "title", 2)
        # No longer a valid test, as there are further titles within embedded data

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_speaker(self, requests_get):
        response = self.client.get('/api/talks/search?from=01/01/01&speaker=' + self.speaker1_slug )
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")

        self.assertContains(response, "James Bond")
        self.assertContains(response, "A future event")

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_venue(self, requests_get):
        response = self.client.get('/api/talks/search?from=01/01/01&venue=' + self.location1)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "Banbury Road")

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_organising_department(self, requests_get):
        response = self.client.get('/api/talks/search?from=01/01/01&organising_department=' + self.department1)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "Chemical Biology")

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_topic(self, requests_get):
        response = self.client.get('/api/talks/search?from=01/01/01&topic=' + self.topic1_uri)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, "Biodiversity")

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_search_sub_organisations(self, requests_get):
        response = self.client.get('/api/talks/search?from=01/01/01&organising_department=' + self.super_department)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "_links")
        self.assertContains(response, "_embedded")
        self.assertContains(response, self.event1_slug)
