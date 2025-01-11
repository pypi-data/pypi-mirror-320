# Standard Library
import re

# Third party
from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from multiselectfield import MultiSelectField

# Local application / specific library imports
from .conf import settings
from kapt_catalog.models import Activity
from kapt_catalog.models.mixins import ASPECT_CHOICES


class ListPluginConf(CMSPlugin):
    tag_name = models.CharField(
        verbose_name=_("Selection numbers"),
        max_length=200,
        help_text=_(
            "Enter one selection number or many numbers separated with commas."
        ),
        blank=True,
        null=True,
    )
    activities = models.ManyToManyField(
        Activity, verbose_name=_("APIDAE objects"), blank=True
    )
    results_per_page = models.IntegerField(
        verbose_name=_("Number of results per page"), null=True, blank=True
    )
    only_translated = models.BooleanField(
        verbose_name=_("Show only objects translated in the page language"),
        default=True,
        blank=True,
    )
    only_aspect = models.PositiveSmallIntegerField(
        verbose_name=_("Show only objects with aspect"),
        choices=[(0, _("Default"))] + list(ASPECT_CHOICES),
        default=0,
    )

    random_sorting = models.BooleanField(null=True, verbose_name=_("Random sorting"))
    opening_date_sorting = models.BooleanField(
        null=True,
        verbose_name=_("Per opening date sorting"),
        help_text=_(
            "If selected, the results will contain only celebrations and manifestations."
        ),
    )
    registration_sorting = models.BooleanField(
        null=True, verbose_name=_("Registered first")
    )
    registration_and_area_sorting = models.BooleanField(
        null=True, verbose_name=_("Registered and in the area first")
    )
    bookable_sorting = models.BooleanField(null=True, verbose_name=_("Booking first"))

    template = models.CharField(
        verbose_name=_("Template"),
        choices=settings.TEMPLATES,
        default=settings.TEMPLATES[0][0],
        max_length=100,
    )
    css_class = models.CharField(
        verbose_name=_("CSS class"),
        choices=settings.CSS_CLASSES,
        max_length=100,
        blank=True,
        null=True,
    )

    # Extensions fields
    filter_form = MultiSelectField(
        verbose_name=_("Filters"),
        choices=settings.FILTER_FORMS,
        blank=True,
        null=True,
        max_length=500,
    )
    context_processor = MultiSelectField(
        verbose_name=_("Extra informations"),
        choices=settings.CONTEXT_PROCESSORS,
        default=settings.DEFAULT_CONTEXT_PROCESSOR,
        blank=True,
        null=True,
        max_length=500,
    )

    class Meta:
        verbose_name = _("APIDAE plugin configuration")
        verbose_name_plural = _("APIDEA plugin configurations")

    def __str__(self):
        if self.tag_name:
            return self.tag_name
        elif self.activities.count() > 0:
            return ", ".join([a.name for a in self.activities.all()])
        else:
            return ""

    def copy_relations(self, oldinstance):
        self.activities.set(oldinstance.activities.all())

    def get_tags_names(self):
        def clean_tag(tag):
            number = re.search(r"\D*(\d*)", tag).group(1)
            return "selection_{}".format(number)

        tags = self.tag_name.replace(" ", "").split(",") if self.tag_name else ""
        tags = map(clean_tag, tags)
        return tags

    def get_results_per_page(self):
        if self.results_per_page not in [None, 0]:
            return self.results_per_page
        else:
            return settings.DEFAULT_CONFIG["results_per_page"]

    def get_random_sorting(self):
        if self.random_sorting is not None:
            return self.random_sorting
        else:
            return settings.DEFAULT_CONFIG["random_sorting"]

    def get_opening_date_sorting(self):
        if self.opening_date_sorting is not None:
            return self.opening_date_sorting
        else:
            return settings.DEFAULT_CONFIG["opening_date_sorting"]

    def get_registration_sorting(self):
        if self.registration_sorting is not None:
            return self.registration_sorting
        else:
            return settings.DEFAULT_CONFIG["registration_sorting"]

    def get_registration_and_area_sorting(self):
        if self.registration_and_area_sorting is not None:
            return self.registration_and_area_sorting
        else:
            return settings.DEFAULT_CONFIG["registration_and_area_sorting"]

    def get_bookable_sorting(self):
        if self.bookable_sorting is not None:
            return self.bookable_sorting
        else:
            return settings.DEFAULT_CONFIG["bookable_sorting"]
