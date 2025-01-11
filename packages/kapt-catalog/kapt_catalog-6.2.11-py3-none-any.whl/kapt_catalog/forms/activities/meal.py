# Third party
from django import forms
from mptt.forms import TreeNodeChoiceField

# Local application / specific library imports
from kapt_catalog.forms.activities.base import ActivityBaseForm
from kapt_catalog.models.activities.meal import (
    InnActivity,
    MealActivity,
    MealActivityProducts,
    TableActivity,
)
from kapt_catalog.models.characteristic import Characteristic
from kapt_catalog.widgets import CharacteristicsMultipleChoiceField


class MealActivityBaseForm(ActivityBaseForm):
    class Meta(ActivityBaseForm.Meta):
        model = MealActivity

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["informations"] = CharacteristicsMultipleChoiceField(
            queryset=Characteristic.objects.get(
                identifier="meal-informations"
            ).get_descendants(),
            level_indicator="",
            required=False,
        )


class MealActivityAdminForm(MealActivityBaseForm):
    pass


class MealActivityProductsBaseForm(forms.ModelForm):
    class Meta:
        model = MealActivityProducts
        exclude = []  # RemovedInDjango18Warning

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.get(
                identifier="meal-activity-products"
            ).get_descendants(),
            level_indicator="",
        )


class MealActivityProductsAdminForm(MealActivityProductsBaseForm):
    pass


class InnActivityBaseForm(MealActivityBaseForm):
    class Meta(MealActivityBaseForm.Meta):
        model = InnActivity

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.filter(
                identifier__in=["meal-type-auberge", "meal-type-inn-ap"]
            ),
            level_indicator="",
        )


class InnActivityAdminForm(InnActivityBaseForm):
    pass


class TableActivityBaseForm(MealActivityBaseForm):
    class Meta(MealActivityBaseForm.Meta):
        model = TableActivity

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.filter(
                identifier__in=["meal-type-table-dhotes"]
            ),
            level_indicator="",
        )


class TableActivityAdminForm(TableActivityBaseForm):
    pass
