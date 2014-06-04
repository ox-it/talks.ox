from django.conf import settings

from .api import PlacesResource


def find_org_descendants(ident):
    api = PlacesResource(settings.API_OX_URL)
    return api.get_organisation_descendants(ident)


def get_info(ident):
    api = PlacesResource(settings.API_OX_URL)
    return api.get_by_id(ident)
