# Standard Library
import datetime
import logging

# Third party
from babel.numbers import format_currency, get_currency_symbol
from django.conf import settings as django_settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import get_language, to_locale, ugettext_lazy as _
from kapt_contact.models import Contact
from kapt_gallery.models import Gallery
from kapt_meta.models import MetaDatasModel
from kapt_utils.models import (
    ActiveModel,
    DatedModel,
    DefaultPolymorphicTranslatableManager,
    PolymorphicTranslatableActiveManager,
    PolymorphicTranslatableManager,
    Reference,
)
from model_utils import Choices
from parler.models import TranslatableModel, TranslatedFields
from parler.utils.context import switch_language
from polymorphic.models import PolymorphicModel
from slugify import slugify as unicode_slugify

# Local application / specific library imports
from kapt_catalog.conf import settings as catalog_settings
from kapt_catalog.constants import PREFECTORAL_LABELLING_CHARACTERISTIC_IDENTIFIER
from kapt_catalog.models.mixins import AspectModel, ContentTypeMixin


class NoAspectManager(PolymorphicTranslatableManager):
    def get_queryset(self):
        return super().get_queryset().filter(aspect__isnull=True)


logger = logging.getLogger("raven")


class ActivityReference(Reference, ContentTypeMixin):
    activity_number = models.PositiveIntegerField(verbose_name=_("Activity number"))
    structure_reference = models.ForeignKey(
        "StructureReference",
        verbose_name=_("Structure reference"),
        on_delete=models.CASCADE,
    )

    # for deduplication of POI objects in Kapt-Catalog
    duplicate_objects = models.ManyToManyField(
        "ActivityReference",
        verbose_name=_("Duplicate objects"),
        through="DuplicateActivityObject",
        blank=True,
        related_name="duplicate_activity_object",
    )

    # categories of activity references (useful for POI for example)
    categories = models.ManyToManyField(
        "ActivityCategory", verbose_name=_("Categories activity"), blank=True
    )

    class Meta:
        verbose_name = _("Activity reference")
        verbose_name_plural = _("Activity references")
        app_label = "kapt_catalog"

    @property
    def name(self):
        activity = self.valid_activity
        if activity.name:
            return activity.name
        else:
            return str(self)

    @property
    def bookable_name(self):
        return self.name

    @cached_property
    def valid_activity(self):
        return self.get_valid_activity()

    def get_valid_activity(self, aspect=None):
        return self.activity_set.get(
            Q(is_active=True),
            Q(aspect=aspect),
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


class DuplicateActivityObject(models.Model):
    first_obj = models.ForeignKey(
        "ActivityReference",
        verbose_name=_("First duplicate object"),
        blank=True,
        null=True,
        related_name="first_obj_duplicateactivityobject_object_set",
        on_delete=models.CASCADE,
    )
    second_obj = models.ForeignKey(
        "ActivityReference",
        verbose_name=_("Second duplicate object"),
        blank=True,
        null=True,
        related_name="second_obj_duplicateactivityobject_object_set",
        on_delete=models.CASCADE,
    )

    # add for import in 10TTS, is '1' if the object is duplicated, '2' if signaled, '0' otherwise
    DUPLICATED_CHOICES = Choices(
        (0, "not_duplicated", _("Not duplicated")),
        (1, "is_duplicated", _("Duplicated")),
        (2, "signaled", _("Signaled")),
    )

    is_duplicated_object = models.PositiveSmallIntegerField(
        verbose_name=_("Duplicated object"),
        default=DUPLICATED_CHOICES.not_duplicated,
        choices=DUPLICATED_CHOICES,
    )

    class Meta:
        verbose_name = _("Duplicate activity")
        verbose_name_plural = _("Duplicate activities")
        app_label = "kapt_catalog"


class ActivityCategory(Reference):
    name = models.CharField(verbose_name=_("Name"), max_length=100)

    class Meta:
        verbose_name = _("Activity Category")
        verbose_name_plural = _("Activity Categories")
        app_label = "kapt_catalog"


# Please ! If you add a GenericRelation or a FK in Activity or a subclass, always test the deletion of the pointed objects.
# A signal exists in order to handle removal.
# You MUST register the signal in projects that extends Activity model such as FNAPBACK


# Activities cannot be translated using modeltranslation because Activity has too many levels of polymorphic childs (it works only with one inheritance level).
# For this reason, Activity fields are localized using django-parler
# We shall use kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
class Activity(
    PolymorphicModel,
    TranslatableModel,
    ActiveModel,
    DatedModel,
    ContentTypeMixin,
    MetaDatasModel,
    AspectModel,
):
    slug = models.SlugField(_("Slug"), max_length=255, blank=True)
    reference_slug = models.SlugField(_("Reference slug"), max_length=255, blank=True)

    reference = models.ForeignKey(
        "ActivityReference",
        verbose_name=_("Reference"),
        help_text=_("The reference will be automatically created on save."),
        on_delete=models.CASCADE,
    )
    structure = models.ForeignKey("Structure", on_delete=models.CASCADE)

    type = models.ForeignKey(
        "Characteristic", related_name="activity_types", on_delete=models.CASCADE
    )

    # TODO: Remove this unused field in catalog v4
    visibility = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Visibility"),
        related_name="activity_visibilities",
        blank=True,
    )

    # Visibility rules
    # --
    # An activity is complete when user has filled a minimum set of required data
    is_complete = models.BooleanField(verbose_name=_("Is complete"), default=False)
    # A activity can be hidden from public visibility if this option is set to False
    is_public = models.BooleanField(verbose_name=_("Is public"), default=True)

    # Take care, if you add something here to check how locales are reinit in kapt_sitra.management.commands.import_sitra_to_kaptravel.catalog.activities_common.update_activity_common
    translations = TranslatedFields(
        name=models.CharField(verbose_name=_("Name"), max_length=255, db_index=True),
        slugid=models.SlugField(_("Slug"), max_length=255, default="", blank=True),
    )

    descriptions = GenericRelation("Description", verbose_name=_("Descriptions"))
    gallery = models.ForeignKey(
        Gallery,
        verbose_name=_("Gallery"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    website = models.URLField(
        verbose_name=_("Website"), max_length=2048, null=True, blank=True
    )
    referent_contact = models.ForeignKey(
        Contact,
        verbose_name=_("Referent contact"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )  # Avoid cascade activity delete

    # Labelling
    labels = models.ManyToManyField(
        "TouristicLabel",
        verbose_name=_("Touristic labels"),
        through="Labelling",
        blank=True,
    )
    main_labelling = models.ForeignKey(
        "Labelling",
        verbose_name=_("Main labelling"),
        blank=True,
        null=True,
        related_name="activity_main_labellings",
        on_delete=models.SET_NULL,
    )
    default_labelling = models.ForeignKey(
        "Labelling",
        verbose_name=_("Default labelling"),
        blank=True,
        null=True,
        related_name="activity_default_labellings",
        on_delete=models.SET_NULL,
    )
    prefectoral_labelling = models.ForeignKey(
        "Labelling",
        verbose_name=_("Prefectoral labelling"),
        blank=True,
        null=True,
        related_name="activity_prefectoral_labellings",
        on_delete=models.SET_NULL,
    )

    """ In the future we will set all the characteristics here, replacing the several m2m with only one:
        The tree structure will be used to categorize characteristics, not the m2m table. """
    characteristics = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Characteristics"),
        blank=True,
        related_name="activity_characteristics",
    )
    means_of_payment = models.ManyToManyField(
        "Characteristic", verbose_name=_("Means of payment"), blank=True
    )
    typologies_promo = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Typologies promo Sitra"),
        blank=True,
        related_name="activity_typologies_promos",
    )
    environment = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Environment"),
        blank=True,
        related_name="activity_environments",
    )
    customer_types = models.ManyToManyField(
        "Characteristic",
        verbose_name=_("Customer types"),
        blank=True,
        related_name="activity_customer_types",
    )

    # The following field sets the number of occurrences of an activity
    # This implies that the resulting number of activities must be managed as a whole
    number_of_occurrences = models.PositiveIntegerField(
        verbose_name=_("Number of occurences"), blank=True, null=True
    )
    linked_activityreferences = models.ManyToManyField(
        "ActivityReference",
        verbose_name=_("Activity reference"),
        related_name="linked_activityreferences",
    )

    # Public
    AGE_UNIT = Choices((0, "month", _("month")), (1, "year", _("year")))

    min_age = models.PositiveSmallIntegerField(
        verbose_name=_("Minimum age"), null=True, blank=True
    )
    max_age = models.PositiveSmallIntegerField(
        verbose_name=_("Maximum age"), null=True, blank=True
    )

    min_age_unit = models.SmallIntegerField(
        verbose_name=_("Minimum age unit"), blank=True, null=True, choices=AGE_UNIT
    )
    max_age_unit = models.SmallIntegerField(
        verbose_name=_("Maximum age unit"), blank=True, null=True, choices=AGE_UNIT
    )

    # Pricing
    is_free = models.BooleanField(default=False, verbose_name=_("Is free"))
    min_price = models.FloatField(verbose_name=_("Minimum price"), null=True)
    max_price = models.FloatField(verbose_name=_("Maximum price"), null=True)
    currency = models.CharField(
        max_length=12, verbose_name=_("Currency"), null=True, blank=True
    )

    # Booking
    booking_url = models.URLField(verbose_name=_("Booking Url"), blank=True, null=True)
    availability_url = models.URLField(
        verbose_name=_("Availability Url"), blank=True, null=True
    )

    can_be_booked_by_owner = models.BooleanField(
        default=False, verbose_name=_("Can be booked by owner")
    )
    can_be_booked_by_organization = models.BooleanField(
        default=False, verbose_name=_("Can be booked by organization")
    )

    # A 'score' field is available to store single score/comment rating average values
    score = models.FloatField(
        verbose_name=_("Average score"), default=0.0, blank=True, null=True
    )

    # Other
    erp_certificate = models.BooleanField(
        verbose_name=_("ERP certification"), default=False
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        app_label = "kapt_catalog"
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")

    def __str__(self):
        try:
            reference = self.reference
            return "#{} {}".format(reference, self.name)
        except ActivityReference.DoesNotExist:
            return self.name

    @property
    def place_name(self):
        logger.warning(
            "Deprecated: activity.place_name has moved to activity.structure.place_name"
        )
        return self.structure.place_name

    @place_name.setter
    def place_name(self, value):
        logger.warning(
            "Deprecated: activity.place_name has moved to activity.structure.place_name"
        )
        self.structure.place_name = value
        self.structure.save()

    def update_main_labelling(self):
        """
        Fill the Activity's main_labelling field with the highest priority non prefectoral Labelling.
        You must call the Activity's save method to commit the changes.
        """
        self.main_labelling = self.labelling_set.main()

        # Update default labelling for retro-compatibility
        self.default_labelling = self.labelling_set.default()

    def update_default_labelling(self):
        """
        Fill the Activity's default_labelling field with the highest priority Labelling.
        You must call the Activity's save method to commit the changes.
        """
        self.default_labelling = self.labelling_set.default()

    def update_prefectoral_labelling(self):
        """
        Fill the Activity's prefectoral_labelling field.
        You must call the Activity's save method to commit the changes.
        """
        self.prefectoral_labelling = self.labelling_set.prefectoral()

        # Update default labelling for retro-compatibility
        self.default_labelling = self.labelling_set.default()

    @classmethod
    def get_child_models(cls):
        return cls.__subclasses__()

    @classmethod
    def get_child_type_choices(cls):  # pragma: no cover
        """
        Return a list of polymorphic types which can be added.
        """
        choices = []
        for model in cls.get_child_models():
            child_type = ContentType.objects.get_for_model(
                model, for_concrete_model=False
            )
            choices.append(
                (
                    child_type.id,
                    model._meta.verbose_name,
                    getattr(model, "HELP_TEXT", None),
                )
            )
        return choices

    @property
    def formatted_reference(self):
        if self.reference:
            return str(self.reference)
        else:  # pragma: no cover
            return "0"

    def get_min_price_display(self):
        """
        Returns the min_price formatted
        for the considered currency and the current locale.
        """
        if self.currency is not None and self.min_price is not None:
            return format_currency(
                self.min_price, self.currency, locale=to_locale(get_language())
            )

    def get_max_price_display(self):
        """
        Returns the max_price formatted
        for the considered currency and the current locale.
        """
        if self.currency is not None and self.max_price is not None:
            return format_currency(
                self.max_price, self.currency, locale=to_locale(get_language())
            )

    def get_currency_display(self):
        if self.currency is not None:
            return get_currency_symbol(self.currency, locale=to_locale(get_language()))

    def save(
        self,
        generate_slug=catalog_settings.ACTIVITY_AUTOMATIC_SLUG_GENERATION,
        *args,
        **kwargs
    ):
        if generate_slug is True:
            self.generate_slug()

        return super().save(*args, **kwargs)

    def fill_name_from_modeltranslation_attribute(
        self, source_object, source_attribute_name
    ):
        from kapt_catalog.models import ActivityTranslation

        for language in django_settings.LANGUAGES:
            language_code = language[0]
            with switch_language(self, language_code):
                source_attribute_name_localized = "{}_{}".format(
                    source_attribute_name, language[0]
                )
                source_value = getattr(
                    source_object, source_attribute_name_localized, None
                )
                if source_value:
                    self.name = source_value
                else:
                    locales = ActivityTranslation.objects.filter(
                        master=self, language_code=language_code
                    ).exclude(language_code=django_settings.LANGUAGE_CODE)
                    if locales.exists():
                        locales.delete()

    @property
    def next_validity_date(self):
        return self.closest_opening_date()

    @property
    def ending_date(self):
        """
        Return ending date only for unique event (One shot)
        """
        periods = self.activityperiod_set.all()

        if len(periods) == 1:
            return periods[0].end
        else:
            return None

    @property
    def all_periods_starting_date(self):
        """
        Return the starting date of the first period for activities with multiple periods
        """
        first_period = self.activityperiod_set.order_by("start").first()
        if first_period is not None:
            return first_period.start

    @property
    def all_periods_ending_date(self):
        """
        Return the ending date of the last period for activities with multiple periods
        """
        last_period = self.activityperiod_set.order_by("start").last()
        if last_period is not None:
            return last_period.end

    def closest_opening_date(self, start_date=None):
        """
        Tries to find the closest opening date for considered event.
        If no start date is passed, the closest opening date is searched from the current date.
        """
        if start_date is None:
            start_date = timezone.now().date()
        # Get all current periods
        periods = self.activityperiod_set.filter(
            start__lte=start_date, end__gte=start_date
        ).order_by("start")
        if periods:
            return start_date
        # Get all opening periods associated with this events
        periods = self.activityperiod_set.filter(start__gte=start_date).order_by(
            "start"
        )
        if periods:
            return periods[0].start
        # Else we fetch all the periods and we return the most recent beginning date
        periods = self.activityperiod_set.order_by("-start")
        if periods:
            return periods[0].start
        return None

    def closest_ending_date(self, start_date=None):
        """
        Tries to find the closest ending date for considered event.
        If no start date is passed, the closest ending date is searched from the current date.
        """
        if start_date is None:
            start_date = timezone.now().date()
        # Get all current periods
        periods = self.activityperiod_set.filter(
            start__lte=start_date, end__gte=start_date
        ).order_by("start")
        if periods:
            return periods[0].end
        # Get all opening periods associated with this events
        periods = self.activityperiod_set.filter(start__gte=start_date).order_by(
            "start"
        )
        if periods:
            return periods[0].end
        # Else we fetch all the periods and we return the most recent beginning date
        periods = self.activityperiod_set.order_by("-start")
        if periods:
            return periods[0].end
        return None

    def insert_closure_period(self, start, end):
        """
        Inserts a closure period in the set of event periods that are related to the considered event.
        The event periods that are in contention with the considered closure period will be deleted or
        reduced.
        """
        # First we try to fetch a potential larger concurrent period
        larger_period = ActivityPeriod.objects.filter(
            activity=self, start__lte=start, end__gte=end
        )
        if larger_period:
            larger_period = larger_period[0]
            # Prepare datetime fields
            older_slot_start = larger_period.start
            younger_slot_end = larger_period.end

            older_period = ActivityPeriod(
                activity=self,
                start=older_slot_start,
                end=start - datetime.timedelta(days=1),
                opening_time=larger_period.opening_time,
                closing_time=larger_period.closing_time,
                further_hourly_informations=larger_period.further_hourly_informations,
            )

            younger_period = ActivityPeriod(
                activity=self,
                start=end + datetime.timedelta(days=1),
                end=younger_slot_end,
                opening_time=larger_period.opening_time,
                closing_time=larger_period.closing_time,
                further_hourly_informations=larger_period.further_hourly_informations,
            )

            # Delete the old one and insert the new periods
            larger_period.delete()
            older_period.save()
            younger_period.save()
            # We can stop the execution here because no other period will be concurrent to the closure period that we consider
            return

        # Then we try to fetch the inner concurrent periods...
        inner_concurrent_periods = ActivityPeriod.objects.filter(
            activity=self, start__gte=start, end__lte=end
        )

        # ... and we delete them
        inner_concurrent_periods.delete()

        # Try to fetch a older period
        older_period = ActivityPeriod.objects.filter(
            Q(activity=self), Q(start__lt=start), Q(end__gte=start), Q(end__lte=end)
        )

        if older_period:
            older_period = older_period[0]

            # Prepare datetime fields
            older_slot_start = older_period.start

            # Prepare the new older period
            new_older_period = ActivityPeriod(
                activity=self,
                start=older_slot_start,
                end=start - datetime.timedelta(days=1),
                opening_time=older_period.opening_time,
                closing_time=older_period.closing_time,
                further_hourly_informations=older_period.further_hourly_informations,
            )

            # Delete the old one and insert the new period
            older_period.delete()
            new_older_period.save()

        # Try to fetch a younger period
        younger_period = ActivityPeriod.objects.filter(
            Q(activity=self), Q(start__gte=start), Q(start__lte=end), Q(end__gt=end)
        )

        if younger_period:
            younger_period = younger_period[0]
            # Prepare datetime fields
            younger_slot_end = younger_period.end

            # Prepare the new older period
            new_younger_period = ActivityPeriod(
                activity=self,
                start=end + datetime.timedelta(days=1),
                end=younger_slot_end,
                opening_time=younger_period.opening_time,
                closing_time=younger_period.closing_time,
                further_hourly_informations=younger_period.further_hourly_informations,
            )

            # Delete the old one and insert the new period
            younger_period.delete()
            new_younger_period.save()

    def generate_slug(self):
        # Fills the translated slugid for each language
        for langcode, langname in django_settings.LANGUAGES:
            if self.has_translation(language_code=langcode):
                # Get the translation model (from django-parler)
                atranslation = self.get_translation(language_code=langcode)
                name = atranslation.name or getattr(self.structure, "name_" + langcode)
                if name is None:
                    # If no name is found for this language (or ''), it means that the activity has no translation for this language
                    continue
                name_slug = (
                    slugify(name)
                    if len(unicode_slugify(name)) == len(slugify(name))
                    else unicode_slugify(name)
                )
                name_slug = name_slug.replace("~", "")
                name_slug = name_slug.replace("--", "-")

                # Update the translated slug (no need to save)
                atranslation.slugid = name_slug

        name = self.name or self.structure.name
        name_slug = (
            slugify(name)
            if len(unicode_slugify(name)) == len(slugify(name))
            else unicode_slugify(name)
        )
        name_slug = name_slug.replace("~", "")
        name_slug = name_slug.replace("--", "-")

        if self.aspect is not None:
            from kapt_catalog.utils.functions import (  # Imported here to avoid cylindric import
                get_aspect_name,
            )

            name_slug += "-{}".format(slugify(get_aspect_name(self.aspect)))

        if (not self.id and not self.slug) or (not self.slug.startswith(name_slug)):
            structure_reference_identifier = self.structure.reference.identifier
            if structure_reference_identifier is not None:
                self.slug = "{}-{}".format(name_slug, structure_reference_identifier)
                self.reference_slug = structure_reference_identifier

            if (
                self.slug is None
                or self.slug == ""
                or (not self.slug.startswith(name_slug))
                or Activity.objects.filter(slug=self.slug).exclude(pk=self.pk).exists()
            ):
                slug_counter = 1
                self.slug = name_slug
                while (
                    Activity.objects.filter(slug=self.slug).exclude(pk=self.pk).exists()
                ):
                    self.slug = "{}-{}".format(name_slug, slug_counter)
                    slug_counter += 1


class ActivityPeriod(models.Model):
    activity = models.ForeignKey(
        Activity, verbose_name=_("Activity"), on_delete=models.CASCADE
    )
    start = models.DateField(verbose_name=_("Start date"))
    end = models.DateField(verbose_name=_("End date"))
    opening_time = models.TimeField(
        verbose_name=_("Opening time"), blank=True, null=True
    )
    closing_time = models.TimeField(
        verbose_name=_("Closing time"), blank=True, null=True
    )
    further_hourly_informations = models.TextField(
        verbose_name=_("Further hourly informations"), blank=True, null=True
    )

    class Meta:
        verbose_name = _("Activity period")
        verbose_name_plural = _("Activity periods")
        app_label = "kapt_catalog"

    def __str__(self):
        return "[{}] {} {}".format(self.activity, self.start, self.end)

    def clean(self):
        # The start date must be lesser or equal than the end date
        if self.start > self.end:
            raise ValidationError(
                _("The start date must be lesser or equal than the end date")
            )

        # An event period must not be in contention with another period
        concurrent_larger_period_exists = ActivityPeriod.objects.filter(
            Q(activity=self.activity),
            ~Q(id=self.id),
            Q(start__lte=self.start),
            Q(end__gte=self.end),
        ).exists()

        inner_concurrent_periods_exists = ActivityPeriod.objects.filter(
            Q(activity=self.activity),
            ~Q(id=self.id),
            Q(start__gte=self.start),
            Q(end__lte=self.end),
        ).exists()

        older_concurrent_periods_exists = ActivityPeriod.objects.filter(
            Q(activity=self.activity),
            ~Q(id=self.id),
            Q(start__lte=self.start),
            Q(end__gte=self.start),
            Q(end__lte=self.end),
        ).exists()

        younger_concurrent_periods_exists = ActivityPeriod.objects.filter(
            Q(activity=self.activity),
            ~Q(id=self.id),
            Q(start__gte=self.start),
            Q(start__lte=self.end),
            Q(end__gte=self.end),
        ).exists()

        coucurrent_period_exist = (
            concurrent_larger_period_exists
            or inner_concurrent_periods_exists
            or older_concurrent_periods_exists
            or younger_concurrent_periods_exists
        )

        if coucurrent_period_exist:
            raise ValidationError(
                _("An activity period must not be in contention with another period")
            )

        # If defined, the opening time must be lesser than the closing time
        if (
            self.opening_time and self.closing_time
        ) and self.opening_time >= self.closing_time:
            raise ValidationError(
                _("The opening time must be lesser than the closing time")
            )

        # A closing time should not be considered as valid if no opening time is defined
        if self.closing_time and not self.opening_time:
            raise ValidationError(
                _("A closing time is not valid if it not comes with an opening time")
            )


class TouristicLabel(ActiveModel):
    name = models.CharField(verbose_name=_("Name"), max_length=200, unique=True)
    logo = models.ImageField(
        verbose_name=_("Icon"), upload_to="labels_logos", null=True, blank=True
    )
    rating_unit = models.ForeignKey(
        "RatingUnit",
        verbose_name=_("Rating unit"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    activity_types = models.ManyToManyField(
        ContentType, verbose_name=_("Activities that can be attached to this Label")
    )  # Prevent a "meal label" to be attached to accommodation activities
    identifier = models.SlugField(
        max_length=100, unique=True, db_index=True, verbose_name=_("Slug identifier")
    )

    class Meta:
        verbose_name = _("Touristic label")
        verbose_name_plural = _("Touristic labels")
        app_label = "kapt_catalog"

    def __str__(self):
        return str(self.name)


class RatingUnit(models.Model):
    """
    A unit used by a label to give a rating.

    It could be: stars, ears, keys, forks, ...
    """

    name = models.CharField(verbose_name=_("Name"), max_length=30)
    icon = models.ImageField(
        verbose_name=_("Icon"), upload_to="rating_units_icons", null=True, blank=True
    )
    identifier = models.SlugField(
        unique=True, db_index=True, verbose_name=_("Slug identifier")
    )

    class Meta:
        verbose_name = _("Rating unit")
        verbose_name_plural = _("Rating units")
        app_label = "kapt_catalog"

    def __str__(self):
        return str(self.name)


class LabellingManager(models.Manager):
    use_for_related_fields = True

    def _l_get_queryset(self):
        get_queryset = (
            self.get_queryset if hasattr(self, "get_queryset") else self.get_query_set
        )
        return get_queryset()

    def main(self):
        """
        Returns the non prefectoral labelling with the highest priority
        """
        qs = self._l_get_queryset().exclude(
            touristic_label__identifier=PREFECTORAL_LABELLING_CHARACTERISTIC_IDENTIFIER
        )
        if qs.count() > 0:
            return qs.order_by("-priority")[0]
        else:
            return None

    def default(self):
        """
        Returns the main labelling if it exists and has a rating
        else returns the prefectoral labelling
        """
        main_labelling = self.main()
        if main_labelling is not None and main_labelling.rating > 0:
            if (
                self.prefectoral()
                and main_labelling.rating >= self.prefectoral().rating
            ):
                return main_labelling
            else:
                return self.prefectoral()
        else:
            return self.prefectoral()

    def prefectoral(self):
        """
        Returns the prefectoral labelling
        """
        try:
            return self._l_get_queryset().get(
                touristic_label__identifier=PREFECTORAL_LABELLING_CHARACTERISTIC_IDENTIFIER
            )
        except ObjectDoesNotExist:
            return None


class Labelling(models.Model):
    """
    The `through` table between Activity and TouristicLabel
    that defines the rating from 1 to 5
    """

    activity = models.ForeignKey(
        "Activity", verbose_name=_("Activity"), on_delete=models.CASCADE
    )
    touristic_label = models.ForeignKey(
        TouristicLabel, verbose_name=_("Touristic label"), on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        default=0, verbose_name=_("Rating")
    )  # The rating is from 1 to 5
    priority = models.PositiveSmallIntegerField(
        verbose_name=_("Priority"),
        help_text=_("0 is high priority, 10 is low priority"),
        default=1,
    )  # 1 is the highest, N the lowest because it is more frequent to add a secondary label than modifying the main label

    objects = LabellingManager()

    class Meta:
        verbose_name = _("Labelling")
        verbose_name_plural = _("Labellings")
        app_label = "kapt_catalog"

    def __str__(self):
        return "{} labelling for activity {}".format(
            self.touristic_label, self.activity
        )
