# Third party
from django.db import models
from django.utils.translation import ugettext_lazy as _
from kapt_utils.models import (
    DefaultPolymorphicTranslatableManager,
    PolymorphicTranslatableActiveManager,
    PolymorphicTranslatableManager,
)
from model_utils import Choices

# Local application / specific library imports
from kapt_catalog.models.activities import Activity, NoAspectManager
from kapt_catalog.models.characteristic import Characteristic


EVENT_REACHES_CHOICES = Choices(
    (0, "residents", _("For residents")),
    (1, "local", _("Local")),
    (2, "departemental", _("Departemental")),
    (3, "regional", _("Regional")),
    (4, "national", _("National")),
    (5, "international", _("International")),
)


class EventActivity(Activity):
    # An event can be classified: reach, event type and categories
    reach = models.PositiveSmallIntegerField(
        choices=EVENT_REACHES_CHOICES, verbose_name=_("Event reach"), db_index=True
    )
    types = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Event types"),
        related_name="event_activity_types",
        blank=True,
    )
    categories = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Event categories"),
        related_name="event_activity_categories",
        blank=True,
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Event activity")
        verbose_name_plural = _("Event activities")
        app_label = "kapt_catalog"

    @property
    def description(self):  # pragma: no cover
        description = self.descriptions.filter(type__identifier="short-description")
        if description.exists():
            return description[0]
        description = self.descriptions.filter(type__identifier="detailed-description")
        if description.exists():
            return description[0]
