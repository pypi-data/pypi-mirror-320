# Third party
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from kapt_utils.models import (
    DefaultPolymorphicTranslatableManager,
    PolymorphicTranslatableActiveManager,
    PolymorphicTranslatableManager,
)
from model_utils import Choices

# Local application / specific library imports
from kapt_catalog.conf import settings as kapt_catalog_settings
from kapt_catalog.core.db.choices import choices_factory
from kapt_catalog.models.activities import Activity, NoAspectManager
from kapt_catalog.models.characteristic import Characteristic


class LeisureActivity(Activity):
    categories = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Categories"),
        related_name="leisure_activity_categories",
        blank=True,
    )
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Max capacity"), null=True
    )
    capacity_min = models.PositiveSmallIntegerField(
        verbose_name=_("Min capacity"), null=True
    )
    informations = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Informations"),
        related_name="leisure_activity_informations",
        blank=True,
    )
    elevation = models.SmallIntegerField(verbose_name=_("Elevation (m)"), null=True)
    distance = models.PositiveIntegerField(verbose_name=_("Distance (km)"), null=True)
    daily_duration = models.PositiveIntegerField(
        verbose_name=_("Daily duration (minute)"), null=True
    )
    roaming_duration = models.PositiveIntegerField(
        verbose_name=_("Roaming duration"), null=True
    )
    duration = models.PositiveIntegerField(
        verbose_name=_("Duration time"), null=True, blank=True
    )
    difficulty = models.SmallIntegerField(
        verbose_name=_("Level of difficulty"),
        choices=choices_factory(Choices(*kapt_catalog_settings.DIFFICULTY)),
        null=True,
        blank=True,
    )
    start_time = models.TimeField(
        verbose_name=_("Departure time"), null=True, blank=True
    )

    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Leisure activity")
        verbose_name_plural = _("Leisure activities")
        app_label = "kapt_catalog"

    def clean(self):
        if self.capacity_min > self.capacity:
            raise ValidationError(
                _("The minimum capacity can not be greater than the capacity")
            )
