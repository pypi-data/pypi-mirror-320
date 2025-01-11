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
from kapt_catalog.conf import settings as local_settings
from kapt_catalog.models.activities import Activity, NoAspectManager
from kapt_catalog.models.characteristic import Characteristic


class MealActivity(Activity):
    capacity = models.PositiveSmallIntegerField(
        verbose_name=_("Capacity"), null=True, blank=True
    )
    products = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Products"),
        through="MealActivityProducts",
        blank=True,
    )
    informations = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Informations"),
        related_name="meal_activity_informations",
        blank=True,
    )
    chef_speciality = models.TextField(
        verbose_name=_("Chef speciality"), null=True, blank=True
    )
    categories = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Categories"),
        related_name="meal_activity_categories",
    )
    specialties = models.ManyToManyField(
        Characteristic,
        verbose_name=_("Specialties"),
        related_name="meal_activity_specialties",
    )

    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Meal activity")
        verbose_name_plural = _("Meal activities")
        app_label = "kapt_catalog"


class MealActivityProducts(models.Model):
    mealactivity = models.ForeignKey(
        "MealActivity", verbose_name=_("Meal activity"), on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "Characteristic", verbose_name=_("Product"), on_delete=models.CASCADE
    )
    distance = models.DecimalField(
        verbose_name=_("Distance between mealactivity and product"),
        max_digits=5,
        decimal_places=2,
    )

    def __str__(self):
        return "{} {} {}".format(self.mealactivity, self.product, self.distance)

    class Meta:
        verbose_name = _("Meal activity product")
        verbose_name_plural = _("Meal activity products")
        unique_together = (("mealactivity", "product"),)
        app_label = "kapt_catalog"


class MealActivitySchedule(models.Model):
    mealactivity = models.ForeignKey(
        "MealActivity",
        verbose_name=_("Meal activity"),
        related_name="schedules",
        on_delete=models.CASCADE,
    )

    MEAL_ACTIVITY_SCHEDULE_TYPES = Choices(*local_settings.MEAL_ACTIVITY_SCHEDULE_TYPES)
    schedule_type = models.IntegerField(
        verbose_name=_("Schedule type"), choices=MEAL_ACTIVITY_SCHEDULE_TYPES
    )

    def __str__(self):
        return "{} - {}".format(
            self.mealactivity.name, self.get_schedule_type_display()
        )

    @property
    def bookable_name(self):
        activity_name = self.mealactivity.name
        bookable_name = "{}".format(self.get_schedule_type_display())
        if activity_name is not None:
            bookable_name += " - {}".format(activity_name)
        return bookable_name

    class Meta:
        verbose_name = _("Meal activity schedule")
        verbose_name_plural = _("Meal activity schedules")
        app_label = "kapt_catalog"
        ordering = ["schedule_type"]


class TableActivity(MealActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Table d'hôtes activity")
        verbose_name_plural = _("Table d'hôtes activities")
        app_label = "kapt_catalog"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.capacity > 15:
            raise ValidationError(_("You have exceed the table d'hôtes max capacity"))


class InnActivity(MealActivity):
    # This should be added with kapt_utils.PolymorphicTranslatableActiveModel but it doesn't work properly, fix if you can
    objects = PolymorphicTranslatableManager()
    default = DefaultPolymorphicTranslatableManager()
    active = PolymorphicTranslatableActiveManager()
    no_aspects = NoAspectManager()

    class Meta:
        verbose_name = _("Inn activity")
        verbose_name_plural = _("Inn activities")
        app_label = "kapt_catalog"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.capacity > 60:
            raise ValidationError(_("You have exceed the auberge max capacity"))
