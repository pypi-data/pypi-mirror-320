# Third party
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Local application / specific library imports
from kapt_catalog.models.activities import Activity


# The implementation of a business tourism Activity has been studied.
# It looks that a standalone object was a better way because we haddn't enough data to fill
# an activity with business and tourism infos (no name, reference, descriptions, gallery, etc etc).


class BusinessTourismService(models.Model):
    activity = models.ForeignKey(
        Activity, verbose_name=_("Activity"), on_delete=models.CASCADE
    )

    characteristics = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Characteristics"),
        blank=True,
        related_name="business_tourism_activity_service_characteristics",
    )
    business_tourism_max_capacity = models.IntegerField(
        verbose_name=_("Business tourism maximum capacity"), null=True, blank=True
    )
    equipped_meeting_rooms_quantity = models.IntegerField(
        verbose_name=_("Equipped meeting rooms quantity"), null=True, blank=True
    )
    adjustable_rooms_quantity = models.IntegerField(
        verbose_name=_("Adjustable rooms quantity"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("Business tourism service")
        verbose_name_plural = _("Business tourism services")
        app_label = "kapt_catalog"


class MeetingRoom(models.Model):
    identifier = models.CharField(
        verbose_name=_("Identifier"), max_length=50, blank=True, null=True
    )  # Identifier would stay the same between two imports (but doesn't exists)
    business_tourism_service = models.ForeignKey(
        "BusinessTourismService",
        verbose_name=_("Business tourism service description"),
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        verbose_name=_("Name"), max_length=150, blank=True, null=True
    )
    descriptions = GenericRelation("Description", verbose_name=_("Descriptions"))
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Max capacity"), blank=True, null=True
    )
    area = models.IntegerField(verbose_name=_("Area"), blank=True, null=True)
    height = models.PositiveSmallIntegerField(
        verbose_name=_("Height"), blank=True, null=True
    )
    natural_lighting = models.BooleanField(
        verbose_name=_("Natural lighting"), default=False
    )
    min_price = models.FloatField(verbose_name=_("Minimum price"), null=True)
    max_price = models.FloatField(verbose_name=_("Maximum price"), null=True)

    class Meta:
        verbose_name = _("Meeting room")
        verbose_name_plural = _("Meeting rooms")
        app_label = "kapt_catalog"

    def __unicode__(self):
        return "%s" % self.name


class RoomLayout(models.Model):
    meeting_room = models.ForeignKey(
        "MeetingRoom", verbose_name=_("Meeting room"), on_delete=models.CASCADE
    )
    capacity = models.PositiveSmallIntegerField(verbose_name=_("Capacity"))
    layout = models.ForeignKey(
        "Characteristic",
        verbose_name=_("Meeting room layout type"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Meeting room layout")
        verbose_name_plural = _("Meeting room layouts")
        app_label = "kapt_catalog"

    def __unicode__(self):
        return "{} - {}".format(self.meeting_room.name, self.layout)
