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


class PackActivity(Activity):
    number_of_days = models.PositiveSmallIntegerField(
        verbose_name=_("Number of days"), null=True, blank=True
    )
    number_of_nights = models.PositiveSmallIntegerField(
        verbose_name=_("Number of nights"), null=True, blank=True
    )

    categories = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Categories"),
        related_name="pack_activity_categories",
        blank=True,
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Pack activity")
        verbose_name_plural = _("Pack activities")
        app_label = "kapt_catalog"
