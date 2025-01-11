# Third party
from django.contrib import admin
from django.utils.translation import ugettext as _
from kapt_utils.admin import ImproveRawIdFieldsForm
from modeltranslation.admin import TranslationGenericStackedInline
from parler.admin import TranslatableAdmin
from polymorphic.admin import PolymorphicChildModelAdmin

# Local application / specific library imports
from kapt_catalog.forms.activities.base import ActivityAdminForm
from kapt_catalog.forms.base import DescriptionAdminForm, LabellingAdminForm
from kapt_catalog.models import Activity, Description, Labelling


#
# This file can't be merged with __init__ file because of circular import
#


# Inlines
class DescriptionInline(TranslationGenericStackedInline):
    model = Description
    extra = 0
    max_num = 2
    form = DescriptionAdminForm
    verbose_name = _("Description")
    verbose_name_plural = _("Descriptions")


class ActivityTouristicLabelInline(admin.TabularInline):
    model = Labelling
    extra = 1
    form = LabellingAdminForm


# Subclasses
class ActivityChildAdmin(
    TranslatableAdmin, PolymorphicChildModelAdmin, ImproveRawIdFieldsForm
):
    raw_id_fields = ("structure", "referent_contact", "main_labelling", "gallery")
    readonly_fields = ("reference",)
    base_model = Activity
    base_form = ActivityAdminForm
    inlines = [DescriptionInline, ActivityTouristicLabelInline]
