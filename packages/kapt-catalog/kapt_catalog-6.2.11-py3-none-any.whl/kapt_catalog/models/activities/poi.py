# Third party
from django.db import models
from django.utils.translation import ugettext_lazy as _
from kapt_utils.models import (
    DefaultPolymorphicTranslatableManager,
    PolymorphicTranslatableActiveManager,
    PolymorphicTranslatableManager,
)

# Local application / specific library imports
from kapt_catalog.models.activities import Activity, NoAspectManager
from kapt_catalog.models.characteristic import Characteristic


class PointOfInterestActivity(Activity):
    categories = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Categories"),
        related_name="poi_activity_categories",
        blank=True,
    )
    themes = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Themes"),
        related_name="poi_activity_themes",
        blank=True,
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Point of interest activity")
        verbose_name_plural = _("Points of interest activities")
        app_label = "kapt_catalog"
