# Third party
from django.db.models import Q
from django.db.utils import ProgrammingError
from django.utils import timezone, translation

# Local application / specific library imports
from .conf.settings import SELECT2_ENABLED
from kapt_catalog.models import ActivityTranslation


if SELECT2_ENABLED:
    try:
        from .fields_select2 import Select2ActivitySearchField as ActivitySearchField
    except ImportError:
        from .fields_select2_legacy import (
            Select2LegacyPageSearchField as ActivitySearchField,
        )
else:
    from django.forms.fields import MultipleChoiceField

    class ActivitySearchField(MultipleChoiceField):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            try:
                # Performance optimization:
                # Fetch directly the translated name from django-parler's table
                active_language = translation.get_language()
                self.choices = [
                    (t.master_id, t.name)
                    for t in ActivityTranslation.objects.filter(
                        (
                            Q(
                                master_id__structure__validity_period__valid_from__lte=timezone.now()
                            )
                            | Q(
                                master_id__structure__validity_period__valid_from__isnull=True
                            )
                        ),
                        (
                            Q(
                                master_id__structure__validity_period__valid_until__gte=timezone.now()
                            )
                            | Q(
                                master_id__structure__validity_period__valid_until__isnull=True
                            )
                        ),
                        master_id__structure__reference__is_active=True,
                        master_id__is_active=True,
                        master_id__is_public=True,
                        language_code=active_language,
                    )
                ]

            except ProgrammingError:
                self.choices = []
