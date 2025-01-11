# Third party
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from kapt_utils.admin import ForeignKeyListMixin, ImproveRawIdFieldsForm
from modeltranslation.admin import (
    TabbedTranslationAdmin,
    TranslationAdmin,
    TranslationGenericStackedInline,
)
from mptt.admin import MPTTModelAdmin

# Local application / specific library imports
from kapt_catalog.forms.base import (
    CharacteristicAdminForm,
    DescriptionAdminForm,
    StructureReferenceForm,
)
from kapt_catalog.forms.structure import (
    StructureAdminForm,
    StructureNearbyLeisureAdminForm,
    StructureNearbyServicesAdminForm,
)
from kapt_catalog.models import Description
from kapt_catalog.models.activities import Activity
from kapt_catalog.models.characteristic import Characteristic
from kapt_catalog.models.reference import StructureReference
from kapt_catalog.models.structure import (
    Structure,
    StructureContact,
    StructureNearbyLeisure,
    StructureNearbyServices,
)


# Inlines
class DescriptionInline(TranslationGenericStackedInline):
    model = Description
    extra = 0
    max_num = 2
    form = DescriptionAdminForm
    verbose_name = _("Description")
    verbose_name_plural = _("Descriptions")


class ActivityInline(ForeignKeyListMixin, admin.TabularInline):
    model = Activity
    readonly_fields = ("name", "edit_link", "delete_link")
    fields = readonly_fields


class StructureContactInline(ForeignKeyListMixin, admin.TabularInline):
    model = StructureContact
    readonly_fields = ("contact", "edit_link")
    fields = ("contact", "edit_link")
    can_delete = True


class StructureNearbyLeisureInline(admin.TabularInline):
    model = StructureNearbyLeisure
    extra = 0
    form = StructureNearbyLeisureAdminForm


class StructureNearbyServicesInline(admin.TabularInline):
    model = StructureNearbyServices
    extra = 0
    form = StructureNearbyServicesAdminForm


class StructureInline(ForeignKeyListMixin, admin.TabularInline):
    model = Structure
    readonly_fields = ("name", "edit_link")
    fields = readonly_fields


# Registered objects
@admin.register(Structure)
class StructureAdmin(ImproveRawIdFieldsForm, TabbedTranslationAdmin):
    raw_id_fields = ("reference", "address")
    list_display = ("reference", "name", "validity_period", "modified_on")
    list_display_links = ("reference", "name")
    search_fields = (
        "reference__id",
        "reference__former_identifier",
        "reference__formatted_identifier",
        "name",
    )
    list_filter = ("created_on", "modified_on", "validity_period")
    form = StructureAdminForm
    inlines = [
        StructureContactInline,
        DescriptionInline,
        StructureNearbyLeisureInline,
        StructureNearbyServicesInline,
        ActivityInline,
    ]


@admin.register(StructureReference)
class StructureReferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "former_identifier", "formatted_identifier")
    search_fields = ("id", "former_identifier")
    form = StructureReferenceForm
    inlines = [StructureInline]


# A filter for characteristic list
class CharacteristicListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("first level characteristics")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "identifier"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        first_level_characteristics = Characteristic.objects.root_nodes()
        characteristic_list = list()
        for characteristic in first_level_characteristics:
            characteristic_list.append((characteristic.identifier, characteristic.name))
        return characteristic_list

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value():
            try:
                mptt_sub_tree = (
                    Characteristic.objects.get(identifier=self.value())
                    .get_descendants(include_self=True)
                    .values_list("id", flat=True)
                )
                return queryset.filter(id__in=mptt_sub_tree)
            except ObjectDoesNotExist:
                pass
        return None


@admin.register(Characteristic)
class CharacteristicAdmin(
    MPTTModelAdmin, TranslationAdmin
):  # DjangoMpttAdmin: Do not remove please
    list_display = (
        "name",
        "identifier",
        "is_active",
        "is_category",
        "in_search_engine",
    )
    search_fields = ["name", "identifier"]
    list_editable = ("is_active", "in_search_engine", "is_category")
    # TODO : put MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en' in settings.py to use name_en instead of name
    prepopulated_fields = {"identifier": ("name",)}
    list_filter = (CharacteristicListFilter,)
    form = CharacteristicAdminForm


@admin.register(StructureContact)
class StructureContactAdmin(ImproveRawIdFieldsForm, admin.ModelAdmin):
    list_display = ("contact", "structure", "is_referent")
    raw_id_fields = ("structure", "contact")
