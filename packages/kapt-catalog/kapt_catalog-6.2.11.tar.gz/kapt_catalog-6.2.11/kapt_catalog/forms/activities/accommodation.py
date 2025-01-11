# Third party
from django import forms
from django.utils.translation import ugettext_lazy as _
from mptt.forms import TreeNodeChoiceField

# Local application / specific library imports
from kapt_catalog.forms.activities.base import ActivityBaseForm
from kapt_catalog.models.activities.accommodation import (
    Bed,
    BnBActivity,
    CamperVanActivity,
    CampingActivity,
    HotelActivity,
    RelayActivity,
    RentalActivity,
)
from kapt_catalog.models.characteristic import Characteristic


class BnBActivityBaseForm(ActivityBaseForm):
    class Meta:
        model = BnBActivity
        exclude = []  # RemovedInDjango18Warning

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.filter(
                identifier__in=["bnb-activity-type"]
            ),
            level_indicator="",
        )


class BnBActivityAdminForm(forms.ModelForm):
    pass


class HotelActivityBaseForm(ActivityBaseForm):
    type = TreeNodeChoiceField(
        queryset=Characteristic.objects.filter(identifier__in=["hotel-activity-type"]),
        level_indicator="",
    )

    class Meta:
        model = HotelActivity
        exclude = []  # RemovedInDjango18Warning


class RentalActivityBaseForm(ActivityBaseForm):
    class Meta:
        model = RentalActivity
        exclude = []  # RemovedInDjango18Warning

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.filter(
                identifier__in=["lodge-activity-type", "gite-sejour-activity-type"]
            ),
            level_indicator="",
        )


class RentalActivityAdminForm(RentalActivityBaseForm):
    pass


class CampingActivityBaseForm(ActivityBaseForm):
    class Meta:
        model = CampingActivity
        exclude = []  # RemovedInDjango18Warning

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.filter(identifier="campsite-activity-type"),
            level_indicator="",
        )


class CampingActivityAdminForm(CampingActivityBaseForm):
    pass


class CamperVanActivityBaseForm(ActivityBaseForm):
    class Meta:
        model = CamperVanActivity
        exclude = []  # RemovedInDjango18Warning

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.filter(
                identifier="campervan-activity-type"
            ),
            level_indicator="",
        )


class CamperVanActivityAdminForm(CamperVanActivityBaseForm):
    pass


class RelayActivityBaseForm(ActivityBaseForm):
    class Meta:
        model = RelayActivity
        fields = (
            "reference",
            "structure",
            "visibility",
            "means_of_payment",
            "referent_contact",
            "type",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.filter(
                identifier__in=["relay-activity-type"]
            ),
            level_indicator="",
        )


class RelayActivityAdminForm(RelayActivityBaseForm):
    pass


class BedAdminForm(forms.ModelForm):
    class Meta:
        model = Bed
        exclude = ("capacity", "reference")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bed_size_categories_ids = (
            Characteristic.objects.get(identifier="accommodation-activity-bed-size")
            .get_children()
            .values_list("id", flat=True)
        )
        bed_sizes = (
            Characteristic.objects.get(identifier="accommodation-activity-bed-size")
            .get_descendants()
            .exclude(id__in=bed_size_categories_ids)
        )
        self.fields["size"] = TreeNodeChoiceField(
            label=_("Size"), queryset=bed_sizes, level_indicator=""
        )
