# Third party
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _
from kapt_utils.models import ActiveModel
from taggit.managers import TaggableManager

# Local application / specific library imports
from .mixins import ContentTypeMixin


class StructureReference(ActiveModel, ContentTypeMixin):
    # An identifier not dependant of the database
    identifier = models.CharField(
        verbose_name=_("Identifier"), max_length=50, null=True, blank=True
    )

    # An identifier in a more 'human readable' format
    formatted_identifier = models.CharField(
        verbose_name=_("Formatted identifier"), max_length=50, null=True, blank=True
    )

    # An identifier used in a previous database or tool
    former_identifier = models.CharField(
        verbose_name=_("Former identifier"),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )

    # Import script datas
    last_import = models.DateTimeField(
        verbose_name=_("Last import from external script"), null=True, blank=True
    )

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this reference belongs to. A reference "
            "will get all permissions granted to each of "
            "its group."
        ),
    )

    # The external lock is a boolean value that can be used in any data retrieving process to forbid
    # the modification of a structure and all of its associated objects.
    # eg. it can be used with kapt-sitra to force the structure and the associated activities to not
    # be updated by the daily-executed script
    external_lock = models.BooleanField(
        verbose_name=_("External lock"), blank=True, default=False
    )

    tags = TaggableManager()

    class Meta:
        verbose_name = _("Structure reference")
        verbose_name_plural = _("Structure references")
        app_label = "kapt_catalog"

    def save(self, *args, **kwargs):
        if self.formatted_identifier is None:
            if self.identifier is not None:
                self.formatted_identifier = self.identifier
            elif self.pk is not None:
                self.formatted_identifier = self.pk

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.formatted_identifier or self.identifier or self.id}"


class OpenSystemReference(models.Model):
    structure_reference = models.OneToOneField(
        StructureReference, on_delete=models.CASCADE
    )
    identifier = models.CharField(verbose_name=_("Identifier"), max_length=100)
    id_integration = models.CharField(
        verbose_name=_("Integration identifier"), max_length=100, null=True, blank=True
    )
    id_basket = models.CharField(
        verbose_name=_("Id basket"), max_length=100, null=True, blank=True
    )

    class Meta:
        verbose_name = _("OpenSystem reference")
        verbose_name_plural = _("OpenSystem references")
        app_label = "kapt_catalog"

    def __str__(self):
        return "{} ({})".format(self.identifier, self.structure_reference.id)


class FairGuestMetaData(models.Model):
    structure_reference = models.OneToOneField(
        StructureReference, on_delete=models.CASCADE
    )

    grade = models.FloatField(verbose_name=_("Grade"))
    label = models.CharField(verbose_name=_("Label"), max_length=100)
    color = models.CharField(verbose_name=_("Color"), max_length=10)
    comments_count = models.PositiveIntegerField(verbose_name=_("Comments count"))
    date_updated = models.BigIntegerField(verbose_name=_("Date updated"))

    class Meta:
        verbose_name = _("FairGUEST reference")
        verbose_name_plural = _("FairGUEST references")
        app_label = "kapt_catalog"

    def __str__(self):
        return "{} {} ({})".format(self.grade, self.label, self.structure_reference.id)
