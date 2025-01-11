# Third party
from django_select2.fields import AutoModelSelect2Field

# Local application / specific library imports
from kapt_catalog.models import Activity


class Select2LegacyActivitySearchField(AutoModelSelect2Field):
    site = None
    search_fields = [
        "translations__name__icontains",
        "structure__name__icontains",
        "reference__former_identifier__icontains",
    ]

    def get_queryset(self):
        return Activity.active.filter(structure__reference__is_active=True)
