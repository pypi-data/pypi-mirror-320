# Third party
from django.contrib import admin
from django.utils.translation import ugettext as _
from kapt_utils.admin.functions import get_admin_url

# Local application / specific library imports
from kapt_catalog.admin.activities.activity import ActivityChildAdmin
from kapt_catalog.forms.activities.accommodation import (
    BedAdminForm,
    BnBActivityAdminForm,
    CamperVanActivityAdminForm,
    CampingActivityAdminForm,
    RelayActivityAdminForm,
    RentalActivityAdminForm,
)
from kapt_catalog.models.activities.accommodation import Bed, Room


class BedInline(admin.TabularInline):
    model = Bed
    extra = 0
    fk_name = "room"
    form = BedAdminForm


class RoomInline(admin.TabularInline):
    model = Room
    fk_name = "accommodation"
    readonly_fields = ("capacity", "admin_change_link")
    fields = ("name", "area", "admin_change_link")

    def admin_change_link(self, obj):
        if obj.id:
            return "<a href='{}' onclick='return showAddAnotherPopup(this);'>{}</a>".format(
                get_admin_url(obj),
                _("Complete beds"),
            )
        else:
            return _("Room must be created before filling beds")

    admin_change_link.short_description = _("Click here to complete beds")
    admin_change_link.allow_tags = True


class OneRoomInline(RoomInline):
    # Only one room can be added, this is usefull for BnB
    extra = 1
    max_num = 1

    verbose_name = _("Room")
    verbose_name_plural = verbose_name


class ManyRoomsInline(RoomInline):
    # Several rooms can be added, this is usefull for Rental
    extra = 1
    verbose_name = _("Room")
    verbose_name_plural = _("Rooms")


class BnBActivityAdmin(ActivityChildAdmin):
    form = BnBActivityAdminForm

    def __init__(self, model, admin_site):
        self.inlines = self.inlines + [OneRoomInline]
        super().__init__(model, admin_site)


class RentalActivityAdmin(ActivityChildAdmin):
    form = RentalActivityAdminForm

    def __init__(self, model, admin_site):
        self.inlines = self.inlines + [ManyRoomsInline]
        super().__init__(model, admin_site)


class CampingActivityAdmin(ActivityChildAdmin):
    form = CampingActivityAdminForm


class CamperVanActivityAdmin(ActivityChildAdmin):
    form = CamperVanActivityAdminForm


class RelayActivityAdmin(ActivityChildAdmin):
    form = RelayActivityAdminForm


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    model = Room
    fields = ("accommodation", "name", "area", "capacity", "gallery")
    raw_id_fields = ("accommodation", "gallery")
    readonly_fields = ("capacity",)
    inlines = [BedInline]
