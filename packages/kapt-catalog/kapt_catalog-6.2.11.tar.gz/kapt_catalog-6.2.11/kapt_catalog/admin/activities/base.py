# Third party
from django.contrib import admin
from django.utils.translation import ugettext as _
from kapt_utils.admin import TabbedTranslationAdmin
from polymorphic.admin import PolymorphicChildModelFilter, PolymorphicParentModelAdmin

# Local application / specific library imports
from kapt_catalog.forms.base import TouristicLabelAdminForm
from kapt_catalog.models.activities import (
    Activity,
    ActivityPeriod,
    Labelling,
    RatingUnit,
    TouristicLabel,
)
from kapt_catalog.models.activities.accommodation import (
    BnBActivity,
    CamperVanActivity,
    CampingActivity,
    RelayActivity,
    RentalActivity,
)
from kapt_catalog.models.activities.event import EventActivity
from kapt_catalog.models.activities.leisure import LeisureActivity
from kapt_catalog.models.activities.meal import InnActivity, MealActivity, TableActivity
from kapt_catalog.models.activities.poi import PointOfInterestActivity


class ActivityPeriodInline(admin.TabularInline):
    model = ActivityPeriod
    extra = 1
    can_delete = True


@admin.register(ActivityPeriod)
class ActivityPeriodAdmin(admin.ModelAdmin):
    list_display = ("activity", "start", "end")


# Parent class
@admin.register(Activity)
class ActivityAdmin(PolymorphicParentModelAdmin):
    from kapt_catalog.admin.activities.accommodation import (
        BnBActivityAdmin,
        CamperVanActivityAdmin,
        CampingActivityAdmin,
        RelayActivityAdmin,
        RentalActivityAdmin,
    )
    from kapt_catalog.admin.activities.event import EventActivityAdmin
    from kapt_catalog.admin.activities.leisure import LeisureActivityAdmin
    from kapt_catalog.admin.activities.meal import (
        InnActivityAdmin,
        MealActivityAdmin,
        TableActivityAdmin,
    )
    from kapt_catalog.admin.activities.poi import PointOfInterestActivityAdmin

    base_model = Activity
    search_fields = ["id"]
    list_display = ("polymorphic_ctype", "reference", "name", "structure")
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        RentalActivity,
        BnBActivity,
        CampingActivity,
        CamperVanActivity,
        RelayActivity,
        LeisureActivity,
        TableActivity,
        InnActivity,
        MealActivity,
        PointOfInterestActivity,
        EventActivity,
    )
    inlines = [ActivityPeriodInline]


# Classic classes
@admin.register(TouristicLabel)
class TouristicLabelAdmin(TabbedTranslationAdmin):
    def has_logo(self, obj):
        return True if obj.logo else False

    has_logo.boolean = True
    has_logo.short_description = _("Has a logo")

    model = TouristicLabel
    list_display = ("identifier", "name", "rating_unit", "has_logo")
    list_display_links = ("identifier", "name")
    search_fields = ["id", "identifier", "name"]
    form = TouristicLabelAdminForm
    # TODO : put MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en' in settings.py to use name_en instead of name
    prepopulated_fields = {"identifier": ("name",)}


@admin.register(RatingUnit)
class LabelRatingUnitAdmin(TabbedTranslationAdmin):
    model = RatingUnit


admin.site.register(Labelling)
