# Django modules
# Third party
# External modules
from django import forms
from django.contrib.contenttypes.models import ContentType
from mptt.forms import TreeNodeChoiceField

# Local application / specific library imports
# Local module
from kapt_catalog.models import Activity, Description, Labelling, TouristicLabel
from kapt_catalog.models.characteristic import Characteristic
from kapt_catalog.models.reference import StructureReference


class StructureReferenceForm(forms.ModelForm):
    class Meta:
        model = StructureReference
        exclude = []  # RemovedInDjango18Warning

    def clean_former_identifier(self):
        former_identifier = self.cleaned_data["former_identifier"]
        if former_identifier == "":
            former_identifier = None
        return former_identifier


# TODO: External objects, might be moved to another file
class DescriptionBaseForm(forms.ModelForm):
    class Meta:
        model = Description
        exclude = []  # RemovedInDjango18Warning

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"] = TreeNodeChoiceField(
            queryset=Characteristic.objects.get(
                identifier="description"
            ).get_descendants(),
            level_indicator="",
        )


class DescriptionAdminForm(DescriptionBaseForm):
    pass


class CharacteristicBaseForm(forms.ModelForm):
    class Meta:
        model = Characteristic
        exclude = []  # RemovedInDjango18Warning


class CharacteristicAdminForm(CharacteristicBaseForm):
    pass


# TODO: Filter choices according to Activity type
class LabellingBaseForm(forms.ModelForm):
    class Meta:
        model = Labelling
        exclude = []  # RemovedInDjango18Warning


class LabellingAdminForm(LabellingBaseForm):
    pass


class TouristicLabelBaseForm(forms.ModelForm):
    activity_types = forms.ModelMultipleChoiceField(
        queryset=ContentType.objects.filter(
            model__in=list(a.__name__.lower() for a in Activity.__subclasses__())
        ),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = TouristicLabel
        exclude = []  # RemovedInDjango18Warning


class TouristicLabelAdminForm(TouristicLabelBaseForm):
    pass
