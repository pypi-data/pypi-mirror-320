# Standard Library
import logging

# Third party
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Manager, Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from kapt_contact.models import Contact
from kapt_gallery.models import Gallery
from kapt_geo.models import Address, Place
from kapt_utils.models import DatedModel
from kapt_validity.models import EphemeralObject, Period
from model_utils import Choices

# Local application / specific library imports
from kapt_catalog.conf.settings import STRUCTURE_CONTACT_TYPE
from kapt_catalog.models.characteristic import Characteristic
from kapt_catalog.models.mixins import AspectModel, ContentTypeMixin
from kapt_catalog.signals import change_referent_contact


logger = logging.getLogger("kapt_catalog")


class StructureManager(Manager):
    pass


class Structure(EphemeralObject, DatedModel, ContentTypeMixin, AspectModel):
    imported_on = models.DateTimeField(
        verbose_name=_("Imported on"), null=True, blank=True
    )
    reference = models.ForeignKey(
        "StructureReference",
        verbose_name=_("Reference"),
        help_text=_("The reference will be automatically created on save."),
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=160, verbose_name=_("Name"), null=True, blank=True
    )
    descriptions = GenericRelation("Description", verbose_name=_("Descriptions"))

    # This Must be moved to Activity
    booking_url = models.URLField(
        verbose_name=_("Booking Url"), blank=True, null=True, max_length=2048
    )

    gallery = models.ForeignKey(
        Gallery,
        verbose_name=_("Gallery"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    spoken_languages = models.ManyToManyField(
        "SpokenLanguage", verbose_name=_("Spoken language"), blank=True
    )  # TODO: why here?
    place_name = models.CharField(
        verbose_name=_("Place name"), max_length=500, blank=True, null=True
    )
    address = models.ForeignKey(
        Address, verbose_name=_("Address"), on_delete=models.CASCADE
    )
    # Question: Should the elevation field be placed in the Address class (kapt-geo) ?
    elevation = models.IntegerField(
        verbose_name=_("Elevation"), blank=True, null=True, db_index=True
    )
    nearby_leisures = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Nearby leisures"),
        through="StructureNearbyLeisure",
        blank=True,
        related_name="structure_nearby_leisures",
    )
    nearby_services = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Nearby services"),
        through="StructureNearbyServices",
        blank=True,
        related_name="structure_nearby_services",
    )
    on_site_services = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("On site services"),
        blank=True,
        related_name="structure_on_site_services",
    )

    contacts = models.ManyToManyField(
        Contact, verbose_name=_("Contacts"), through="StructureContact", blank=True
    )

    class Meta:
        verbose_name = _("Structure")
        verbose_name_plural = _("Structures")
        app_label = "kapt_catalog"
        # unique together = (reference and validity_period)

    def __str__(self):
        if not self.pk:
            return "Structure without reference"
        else:
            return "{} - {}".format(self.reference, self.name)

    def save(self, *args, **kwargs):
        # TODO: Remove this code when we will remove validity period attribute
        if self.pk is None and not hasattr(self, "validity_period"):
            self.validity_period = Period.objects.all()[0]

        super().save(*args, **kwargs)

    @property
    def referent_contact(self):
        try:
            return self.structurecontact_set.get(is_referent=True).contact
        except ObjectDoesNotExist:
            return None

    @property
    def active_activities_count(self):
        return self.activity_set.filter(is_active=True).count()

    @property
    def first_valid_activity(self):
        activity_set = self.activity_set.filter(
            Q(is_active=True),
            Q(
                Q(structure__validity_period__valid_from__lte=timezone.now()),
                Q(structure__validity_period__valid_until__gte=timezone.now()),
            )
            | Q(
                Q(structure__validity_period__valid_from__isnull=True),
                Q(structure__validity_period__valid_until__gte=timezone.now()),
            )
            | Q(
                Q(structure__validity_period__valid_from__isnull=True),
                Q(structure__validity_period__valid_until__isnull=True),
            ),
        )

        if activity_set.exists():
            return activity_set[0]
        else:
            raise ObjectDoesNotExist

    def set_referent_contact(self, contact_pk):
        """
        The the contact with the pk `contact_pk` as referent contact of the structure `structure_pk`.
        """
        # Get the current referent
        try:
            current_referent = self.structurecontact_set.get(is_referent=True)
        except ObjectDoesNotExist:
            current_referent = None
        # Remove all referent states
        self.structurecontact_set.update(is_referent=False)

        try:
            new_referent = self.structurecontact_set.get(contact_id=contact_pk)
        except ObjectDoesNotExist:
            return None

        new_referent.is_referent = True
        new_referent.save()
        change_referent_contact.send(
            sender=self.__class__,
            current_referent=current_referent,
            new_referent=new_referent,
        )

        return new_referent

    def set_address(
        self, locality, locality_id, address1, address2, latitude, longitude, altitude
    ):
        selected_locality = Place.objects.get(geonameid=locality_id)
        address = None

        if locality is not None:
            if self.address_id is not None:
                # Update existing Address
                address = self.address
                address.place = selected_locality
                address.address1 = address1
                if address2 is not None:
                    address.address2 = address2
                address.latitude = latitude
                address.longitude = longitude

            else:  # pragma: no cover
                # Create an Address (this should not happen)
                address = Address(
                    place=selected_locality,
                    address1=address1,
                    latitude=latitude,
                    longitude=longitude,
                )

                if address2 is not None:
                    address.address2 = address2

            address.save()
            self.address = address

            if altitude is not None:
                self.elevation = altitude


class StructureNearbyLeisure(models.Model):
    structure = models.ForeignKey(
        "Structure", verbose_name=_("Structure"), on_delete=models.CASCADE
    )
    leisure = models.ForeignKey(
        Characteristic, verbose_name=_("Leisure"), on_delete=models.CASCADE
    )
    distance = models.DecimalField(
        verbose_name=_("Distance between leisure and structure"),
        max_digits=5,
        decimal_places=2,
    )

    class Meta:
        app_label = "kapt_catalog"
        unique_together = ["structure", "leisure"]

    def __str__(self):
        return self.leisure.name


class StructureNearbyServices(models.Model):
    structure = models.ForeignKey(
        "Structure", verbose_name=_("Structure"), on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Characteristic, verbose_name=_("Service"), on_delete=models.CASCADE
    )
    distance = models.DecimalField(
        verbose_name=_("Distance between service and structure"),
        max_digits=5,
        decimal_places=2,
    )

    class Meta:
        app_label = "kapt_catalog"
        unique_together = ["structure", "service"]

    def __str__(self):
        return self.service.name


class StructureContact(models.Model):
    TYPE = Choices(*STRUCTURE_CONTACT_TYPE)
    structure = models.ForeignKey(
        Structure, verbose_name=_("Structure"), on_delete=models.CASCADE
    )
    contact = models.ForeignKey(
        Contact, verbose_name=_("Contact"), on_delete=models.CASCADE
    )
    type = models.IntegerField(
        verbose_name=_("Contact type for this structure"),
        choices=TYPE,
        null=True,
        blank=True,
    )
    is_referent = models.BooleanField(verbose_name=_("Is referent"), default=True)

    class Meta:
        app_label = "kapt_catalog"
        unique_together = ("structure", "contact")
        verbose_name = _("Structure contact")
        verbose_name_plural = _("Structure contacts")

    def __str__(self):
        return "{} - #{}".format(self.contact.__unicode__(), self.structure.id)

    def clean(self):
        # A referent contact already exists
        if (
            self.is_referent
            and StructureContact.objects.filter(
                structure=self.structure, is_referent=True
            )
            .exclude(contact=self.contact)
            .exists()
        ):
            raise ValidationError(_("Only one contact can be set as 'referent'"))
