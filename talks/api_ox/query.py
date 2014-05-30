from django.conf import settings

from .api import PlacesResource


def find_org_descendants(oxpoints_id):
    api = PlacesResource(settings.API_OX_URL)
    return api.get_organisation_descendants('oxpoints:{ident}'.format(ident=oxpoints_id))


def find_spatial_descendants(oxpoints_id):
    pass


def get_info(oxpoints_id):
    api = PlacesResource(settings.API_OX_URL)
    return api.get_by_id('oxpoints:{ident}'.format(ident=oxpoints_id))
