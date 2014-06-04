from django.conf import settings

from .api import PlacesResource
from talks.api_ox.api import DatesResource


def find_org_descendants(ident):
    api = PlacesResource(settings.API_OX_URL)
    return api.get_organisation_descendants(ident)


def get_info(ident):
    api = PlacesResource(settings.API_OX_URL)
    return api.get_by_id(ident)


def get_oxford_date(py_date):
    api = DatesResource(settings.API_OX_URL)
    return api.get_oxford_date(py_date)
