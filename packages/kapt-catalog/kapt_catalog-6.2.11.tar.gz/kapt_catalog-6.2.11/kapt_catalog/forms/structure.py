# Third party
from django import forms

# Local application / specific library imports
from kapt_catalog.models import (
    Structure,
    StructureNearbyLeisure,
    StructureNearbyServices,
)
from kapt_catalog.utils.forms import JQuerySelectMultipleForm


class StructureAdminForm(forms.ModelForm, JQuerySelectMultipleForm):
    class Meta:
        model = Structure
        exclude = []  # RemovedInDjango18Warning


class StructureNearbyLeisureAdminForm(forms.ModelForm):
    class Meta:
        model = StructureNearbyLeisure
        exclude = []  # RemovedInDjango18Warning


class StructureNearbyServicesAdminForm(forms.ModelForm):
    class Meta:
        model = StructureNearbyServices
        exclude = []  # RemovedInDjango18Warning
