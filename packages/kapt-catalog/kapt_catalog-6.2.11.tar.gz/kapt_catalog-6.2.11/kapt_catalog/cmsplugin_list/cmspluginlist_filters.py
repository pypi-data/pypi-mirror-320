# Third party
from django.core.exceptions import ObjectDoesNotExist
from kapt_geo.models import Place


def geonameid(qs, parameters):
    # Geo filters
    locality_id = parameters.pop("locality_id", None)

    # Handles per locality filtering
    if locality_id and len(locality_id) and locality_id[0] != "":
        try:
            locality = Place.objects.get(geonameid=locality_id[0])
        except ObjectDoesNotExist:
            pass
        else:
            qs = qs.filter(structure__address__place=locality)

    return qs


def free_only(qs, parameters):
    # Free only filter
    free_only = parameters.pop("free_only", None)

    # Display only activities that have no min price
    if free_only:
        qs = qs.filter(min_price__isnull=True, max_price__isnull=True)

    return qs
