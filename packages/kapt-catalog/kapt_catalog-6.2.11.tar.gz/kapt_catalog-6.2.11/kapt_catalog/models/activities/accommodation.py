# Third party
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from kapt_gallery.models import Gallery
from kapt_utils.models import (
    DefaultPolymorphicTranslatableManager,
    PolymorphicTranslatableActiveManager,
    PolymorphicTranslatableManager,
    Reference,
)
from model_utils import Choices

# Local application / specific library imports
from kapt_catalog.conf import settings as local_settings
from kapt_catalog.conf.settings import (
    ACCOMMODATION_ACTIVITY_AUTOMATIC_CAPACITY_UPDATE as AUTOMATIC_CAPACITY_UPDATE,
    ACCOMMODATION_ACTIVITY_AUTOMATIC_EDGE_ROOM_CAPACITIES_UPDATE as AUTOMATIC_EDGE_ROOM_CAPACITIES_UPDATE,
    ACCOMMODATION_ACTIVITY_AUTOMATIC_ROOM_QUANTITY_UPDATE as AUTOMATIC_ROOM_QUANTITY_UPDATE,
)
from kapt_catalog.constants import ACCOMMODATION_UNLIMITED_CAPACITY
from kapt_catalog.models.activities import Activity, NoAspectManager
from kapt_catalog.models.characteristic import Characteristic
from kapt_catalog.models.mixins import ContentTypeMixin
from kapt_catalog.signals import bnb_capacity_changed


class AccommodationActivity(Activity):
    TOURIST_TAX = Choices(
        (0, "no_tax", _("No tax")),
        (1, "included", _("Included in the price")),
        (2, "not_included", _("Not included in the price")),
    )

    HOUSING_TYPES = Choices(*local_settings.HOUSING_TYPES)
    housing_type = models.IntegerField(
        verbose_name=_("Property type"), blank=True, null=True, choices=HOUSING_TYPES
    )

    # The 'capacity' is the sum of the capacities of each room
    # Note: can be computed according to the beds quantity. Max = 14 except for campings !
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Capacity"),
        null=True,
        help_text=_(
            "The capacity will be automatically computed according to the beds you specified"
        ),
    )

    # The 'min_capacity_per_room' and the 'max_capacity_per_room' are respectively related to
    # the minimum capacity and the maximum capacity proposed bu the rooms of the activity.
    min_capacity_per_room = models.PositiveIntegerField(
        verbose_name=_("Minimum capacity per room"),
        null=True,
        help_text=_(
            "This value will be automatically computed according to the beds you specified"
        ),
    )
    max_capacity_per_room = models.PositiveIntegerField(
        verbose_name=_("Maximum capacity per room"),
        null=True,
        help_text=_(
            "This value will be automatically computed according to the beds you specified"
        ),
    )

    max_capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Max Capacity"), null=True
    )

    area = models.PositiveIntegerField(verbose_name=_("Area"), null=True, db_index=True)
    number_of_floors = models.PositiveSmallIntegerField(
        verbose_name=_("Number of floors"), default=1
    )  # TODO: is this usefull for BnB and Campsite?
    number_of_rooms = models.SmallIntegerField(
        verbose_name=_("Number of rooms"), null=True, blank=True
    )

    is_light_construction = models.BooleanField(
        verbose_name=_("Light construction"), default=False
    )  # Hébergement léger: Habitation légère de loisirs: http://fr.wikipedia.org/wiki/Habitation_l%C3%A9g%C3%A8re_de_loisirs
    unusual_accommodation = models.BooleanField(
        verbose_name=_("Unusual accommodation"), default=False
    )

    # OK, with categories, TODO: Divide characteristics according to activity last sub class !
    # Ex: "Catering is not available for Resting places and BnB (breakfast is always included)"
    facilities = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Facilities"),
        related_name="accommodation_activity_facilities",
        blank=True,
    )
    technical_characteristics = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Technical characteristics"),
        related_name="accommodation_activity_technical_characteristics",
        blank=True,
    )
    services = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Services"),
        related_name="accommodation_activity_services",
        blank=True,
    )

    # Outdoor values
    land_surface = models.CharField(
        verbose_name=_("Land surface"), max_length=20, blank=True, null=True
    )
    garden_surface = models.CharField(
        verbose_name=_("Garden surface"), max_length=20, blank=True, null=True
    )
    pool_dimension = models.CharField(
        verbose_name=_("Pool dimension"), max_length=20, blank=True, null=True
    )
    patio_surface = models.CharField(
        verbose_name=_("Patio surface"), max_length=20, blank=True, null=True
    )

    # Accommodation specific pricing infos
    tourist_tax = models.IntegerField(
        verbose_name=_("Tourist tax type"), blank=True, null=True, choices=TOURIST_TAX
    )
    deposit = models.FloatField(verbose_name=_("Deposit"), null=True, blank=True)
    pets_deposit = models.FloatField(
        verbose_name=_("Pets deposit"), null=True, blank=True
    )

    # Accommodation check-in check-out time
    check_in_time = models.TimeField(
        verbose_name=_("Check-in time"), null=True, blank=True
    )
    check_out_time = models.TimeField(
        verbose_name=_("Check-out time"), null=True, blank=True
    )
    min_stay_duration = models.PositiveIntegerField(
        verbose_name=_("Minimum number of nights"), null=True, blank=True
    )
    arrival_days = models.ManyToManyField(
        "AccommodationArrivalDay", verbose_name=_("Arrival days")
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    # TODO: what is social convention ?
    # social_convention = models.ForeignKey(Characteristic, related_name='accommodation_social_convention+', null=True)

    class Meta:
        verbose_name = _("Accommodation activity")
        verbose_name_plural = _("Accommodation activities")
        app_label = "kapt_catalog"

    def save(
        self,
        update_capacity=AUTOMATIC_CAPACITY_UPDATE,
        update_number_of_rooms=AUTOMATIC_ROOM_QUANTITY_UPDATE,
        update_edge_room_capacities=AUTOMATIC_EDGE_ROOM_CAPACITIES_UPDATE,
        *args,
        **kwargs
    ):
        if isinstance(self, CampingActivity):
            return super().save(*args, **kwargs)
        else:
            capacity_changed = False
            if update_capacity is True:
                old_capacity = self.capacity
                if self.capacity != self.compute_capacity():
                    capacity_changed = True

            if update_number_of_rooms is True:
                self.number_of_rooms = self.room_set.filter(
                    reference__is_active=True
                ).count()

            if update_edge_room_capacities:
                self.compute_edge_room_capacities()

            super_result = super().save(*args, **kwargs)

            if capacity_changed and isinstance(self, BnBActivity):
                bnb_capacity_changed.send(
                    sender=self.__class__,
                    instance=self,
                    old_capacity=old_capacity,
                    new_capacity=self.capacity,
                )

            return super_result

    @property
    def is_single_storey(self):
        # Plain pied
        return self.number_of_floors == 1

    @property
    def maximum_capacity(self):
        return ACCOMMODATION_UNLIMITED_CAPACITY

    def compute_capacity(self):
        accommodation_rooms = self.room_set.filter(
            capacity__gt=0, reference__is_active=True
        )
        if accommodation_rooms.exists():
            self.capacity = 0
            for room in accommodation_rooms:
                self.capacity += room.capacity
        else:
            self.capacity = 0
        return self.capacity

    def compute_edge_room_capacities(self):
        accommodation_rooms = list(
            self.room_set.filter(capacity__gt=0, reference__is_active=True).order_by(
                "capacity"
            )
        )
        if accommodation_rooms:
            self.min_capacity_per_room = accommodation_rooms[0].capacity
            self.max_capacity_per_room = accommodation_rooms[-1].capacity
        return (self.min_capacity_per_room, self.max_capacity_per_room)


class AccommodationArrivalDay(models.Model):
    # Duplicated from kapt_pricing so the mapping is easy

    # Choices are based on isocalendar() days values in python datetime module
    DAYS_VALUES_CHOICES = Choices(
        (1, "monday", _("Monday")),
        (2, "tuesday", _("Tuesday")),
        (3, "wednesday", _("Wednesday")),
        (4, "thursday", _("Thursday")),
        (5, "friday", _("Friday")),
        (6, "saturday", _("Saturday")),
        (7, "sunday", _("Sunday")),
    )
    day = models.PositiveSmallIntegerField(
        choices=DAYS_VALUES_CHOICES, verbose_name=_("Day"), unique=True
    )

    class Meta:
        app_label = "kapt_catalog"
        verbose_name = _("Arrival day")
        verbose_name_plural = _("Arrival days")

    def __str__(self):
        return self.get_day_display()


class BnBActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Bed & Breakfast activity")
        verbose_name_plural = _("Bed & Breakfast activities")
        app_label = "kapt_catalog"

    def clean(self):
        from django.core.exceptions import ValidationError

        if (
            self.maximum_capacity != ACCOMMODATION_UNLIMITED_CAPACITY
            and self.capacity > self.maximum_capacity
        ):
            raise ValidationError(
                _("Your accommodation exceed the maximum capacity value")
            )

    @property
    def maximum_capacity(self):
        return local_settings.MAXIMUM_CAPACITY_PER_BNB


class RentalActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Rental activity")
        verbose_name_plural = _("Rental activities")
        app_label = "kapt_catalog"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.maximum_capacity != ACCOMMODATION_UNLIMITED_CAPACITY:
            if (
                self.erp_certificate is False
                and self.capacity
                > local_settings.MAXIMUM_CAPACITY_PER_RENTAL_WITHOUT_ERP
            ):
                raise ValidationError(
                    _(
                        "Your accommodation exceed the maximum capacity value. "
                        "The maximum allowed capacity for a rental without ERP certification is: "
                    )
                    + str(local_settings.MAXIMUM_CAPACITY_PER_RENTAL_WITHOUT_ERP)
                )
            elif self.capacity > self.maximum_capacity:
                raise ValidationError(
                    _("Your accommodation exceed the maximum capacity value")
                )

    @property
    def maximum_capacity(self):
        if self.erp_certificate:
            return local_settings.MAXIMUM_CAPACITY_PER_RENTAL_WITH_ERP
        else:
            return local_settings.MAXIMUM_CAPACITY_PER_RENTAL_WITHOUT_ERP


class CampingActivity(AccommodationActivity):
    number_of_pitches = models.PositiveSmallIntegerField(
        verbose_name=_("Number of pitches"), default=0
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Camping activity")
        verbose_name_plural = _("Camping activities")
        app_label = "kapt_catalog"


class CamperVanActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Camper van activity")
        verbose_name_plural = _("Camper van activities")
        app_label = "kapt_catalog"


class HotelActivity(AccommodationActivity):
    ranked_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Ranked rooms quantity"), null=True, blank=True
    )  # nombreChambresClassees
    hotel_declared_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Hotel declared rooms quantity"), null=True, blank=True
    )
    single_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Single rooms quantity"), null=True, blank=True
    )  # nombreChambresSimples
    double_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Double rooms quantity"), null=True, blank=True
    )  # nombreChambresDoubles
    suite_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Suite rooms quantity"), null=True, blank=True
    )  # nombreSuites
    reduced_mobility_rooms_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Reduced mobility rooms quantity"), null=True, blank=True
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Hotel activity")
        verbose_name_plural = _("Hotel activities")
        app_label = "kapt_catalog"


class HolidayVillageActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Holiday village activity")
        verbose_name_plural = _("Holiday village activities")
        app_label = "kapt_catalog"


class RelayActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Relay activity")
        verbose_name_plural = _("Relay activities")
        app_label = "kapt_catalog"

    @property
    def maximum_capacity(self):
        return local_settings.MAXIMUM_CAPACITY_PER_RELAY


class YouthHostelActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Youth hostel activity")
        verbose_name_plural = _("Youth hostel activities")
        app_label = "kapt_catalog"


class HomestayActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Homestay activity")
        verbose_name_plural = _("Homestay activities")
        app_label = "kapt_catalog"


class RiadActivity(AccommodationActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Riad activity")
        verbose_name_plural = _("Riad activities")
        app_label = "kapt_catalog"


class RoomReference(Reference, ContentTypeMixin):
    room_number = models.PositiveIntegerField(verbose_name=_("Room number"))
    activity_reference = models.ForeignKey(
        "ActivityReference",
        verbose_name=_("Activity reference"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Room reference")
        verbose_name_plural = _("Room references")
        app_label = "kapt_catalog"

    @property
    def name(self):
        room = self.valid_room
        if room is not None and room.name:
            return room.name
        else:
            return "{} {}".format(_("Room"), self.room_number)

    @property
    def bookable_name(self):
        activity_name = self.activity_reference.bookable_name
        bookable_name = "{}".format(self.name)
        if activity_name is not None:
            bookable_name += " - {}".format(activity_name)
        return bookable_name

    @cached_property
    def valid_room(self):
        return self.get_valid_room()

    def get_valid_room(self):
        try:
            room = self.room_set.get(
                Q(accommodation__is_active=True),
                Q(
                    Q(
                        accommodation__structure__validity_period__valid_from__lte=timezone.now()
                    ),
                    Q(
                        accommodation__structure__validity_period__valid_until__gte=timezone.now()
                    ),
                )
                | Q(
                    Q(
                        accommodation__structure__validity_period__valid_from__isnull=True
                    ),
                    Q(
                        accommodation__structure__validity_period__valid_until__gte=timezone.now()
                    ),
                )
                | Q(
                    Q(
                        accommodation__structure__validity_period__valid_from__isnull=True
                    ),
                    Q(
                        accommodation__structure__validity_period__valid_until__isnull=True
                    ),
                ),
            )

        except ObjectDoesNotExist:
            room = None
        return room


class Room(models.Model, ContentTypeMixin):
    """
    Represents an accommodation room.
    """

    reference = models.ForeignKey(
        "RoomReference",
        verbose_name=_("Reference"),
        help_text=_("The reference will be automatically created on save."),
        on_delete=models.CASCADE,
    )
    accommodation = models.ForeignKey(
        AccommodationActivity, verbose_name=_("Accommodation"), on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name=_("Name"), max_length=150, blank=True, null=True
    )

    # Translators: the number that identify one room
    number = models.PositiveIntegerField(verbose_name=_("Room number"), blank=True)
    area = models.PositiveSmallIntegerField(
        verbose_name=_("Area"), blank=True, null=True
    )
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Capacity"),
        default=0,
        help_text=_(
            "The capacity will be automatically computed according to the beds you specified"
        ),
    )  # TODO: zero or null?

    facilities = models.ManyToManyField(
        Characteristic, verbose_name=_("Facilities"), related_name="rooms", blank=True
    )
    gallery = models.ForeignKey(
        Gallery,
        verbose_name=_("Gallery"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    descriptions = GenericRelation("Description", verbose_name=_("Descriptions"))

    class Meta:
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")
        app_label = "kapt_catalog"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Set the number field by increasing by 1 the latest room
        number for this accommodation.
        """
        if not self.id:
            if self.accommodation.room_set.exists():
                last_room = self.accommodation.room_set.filter(
                    reference__is_active=True
                ).order_by("-number")[0]
                self.number = last_room.number + 1
            else:
                self.number = 1

        if not self.name:
            if self.number:
                self.name = str(self.number)

        super().save()

    def compute_capacity(self):
        beds = self.bed_set.all()
        self.capacity = 0
        for bed in beds:
            self.capacity += bed.capacity
        self.save()
        self.accommodation.save()


class BedReference(Reference, ContentTypeMixin):
    bed_number = models.PositiveIntegerField(verbose_name=_("Bed number"))
    room_reference = models.ForeignKey(
        "RoomReference", verbose_name=_("Room reference"), on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Bed reference")
        verbose_name_plural = _("Bed references")
        app_label = "kapt_catalog"

    @property
    def bookable_name(self):
        room_name = self.room_reference.bookable_name
        bed_name = None
        beds = self.bed_set.all()
        if beds.exists():
            bed = beds[0]
            bed_name = "{}".format(bed.size)
        bookable_name = ""
        if bed_name:
            bookable_name += "{} - ".format(bed_name)
        else:
            bookable_name += _("Bed {} - ").format(self.bed_number)
        if room_name:
            bookable_name += "{}".format(room_name)
        return bookable_name


class Bed(models.Model, ContentTypeMixin):
    reference = models.ForeignKey(
        "BedReference",
        verbose_name=_("Reference"),
        help_text=_("The reference will be automatically created on save."),
        on_delete=models.CASCADE,
    )
    room = models.ForeignKey(Room, verbose_name=_("Room"), on_delete=models.CASCADE)
    size = models.ForeignKey(
        Characteristic,
        verbose_name=_("Size"),
        related_name="bed_size",
        on_delete=models.CASCADE,
    )
    capacity = models.PositiveSmallIntegerField(verbose_name=_("Capacity"), default=2)
    is_extra_bed = models.BooleanField(verbose_name=_("Extra bed"), default=False)

    class Meta:
        verbose_name = _("Bed")
        verbose_name_plural = _("Beds")
        app_label = "kapt_catalog"

    def __str__(self):
        return "{}, {}".format(self.room.name, self.size)

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError

        if not self.id:
            try:
                self.size
            except ObjectDoesNotExist:
                raise ValidationError(_("You must fill a value for the field 'size'"))

            if (
                self.room.accommodation.maximum_capacity
                != ACCOMMODATION_UNLIMITED_CAPACITY
            ):
                new_bed_capacity = int(self.size.parent.value)
                other_beds_capacity = Bed.objects.filter(
                    room__accommodation=self.room.accommodation,
                    room__reference__is_active=True,
                ).aggregate(capacity_sum=Sum("capacity"))
                if other_beds_capacity["capacity_sum"] > 0:
                    if (
                        other_beds_capacity["capacity_sum"] + new_bed_capacity
                    ) > self.room.accommodation.maximum_capacity:
                        raise ValidationError(
                            _(
                                "Your accommodation raised the maximum capacity value, you can't add a new bed"
                            )
                        )

    def save(self, compute_room_capacity=True, *args, **kwargs):
        # Compute the capacity based on beds quantity
        self.capacity = int(self.size.parent.value)

        super().save()

        if compute_room_capacity:
            self.room.compute_capacity()

    def delete(self, *args, **kwargs):
        super().delete()
        self.room.compute_capacity()
