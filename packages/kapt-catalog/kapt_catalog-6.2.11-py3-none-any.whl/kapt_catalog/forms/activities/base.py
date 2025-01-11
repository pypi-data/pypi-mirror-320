# Third party
from django import forms
from django.utils.translation import ugettext_lazy as _
from parler.forms import TranslatableModelForm

# Local application / specific library imports
from kapt_catalog.models import (
    Activity,
    ActivityReference,
    Characteristic,
    Labelling,
    TouristicLabel,
)


class ActivityBaseForm(TranslatableModelForm):
    # Just for display
    activity_reference = forms.CharField(
        label=_("Reference"),
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
        required=False,
    )

    class Meta:
        abstract = True
        model = Activity
        fields = (
            "structure",
            "type",
            "name",
            "visibility",
            "website",
            "means_of_payment",
            "referent_contact",
        )
        excludes = (
            "reference",
            "linked_structurereferences_formeridentifiers_ids",
            "linked_events_formeridentifiers_ids",
        )
        widgets = {"structure": forms.widgets.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields["activity_reference"].initial = (
                self.instance.reference.formatted_identifier
                or self.instance.reference.former_identifier
            )
        except ActivityReference.DoesNotExist:
            pass

        self.fields["visibility"] = forms.ModelMultipleChoiceField(
            label=_("Visibility"),
            help_text=_("This activity will only appear on the media checked."),
            queryset=Characteristic.objects.get(
                identifier="visibility"
            ).get_active_descendants(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )
        self.fields["means_of_payment"] = forms.ModelMultipleChoiceField(
            label=_("Means of payment"),
            queryset=Characteristic.objects.get(
                identifier="payment-mean"
            ).get_active_descendants(),
            widget=forms.CheckboxSelectMultiple,
        )

        self.fields["touristic_labels"] = forms.ModelMultipleChoiceField(
            label=_("Touristic labels"),
            queryset=TouristicLabel.active.all(),
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )

    def save(self, force_insert=False, force_update=False, commit=True):
        self.instance = super().save(commit=False)

        if commit:
            self.instance.save()
            self.save_m2m()

            # Clear all relations before adding the new ones
            Labelling.objects.filter(activity=self.instance).delete()
            if "touristic_labels" in self.cleaned_data:
                for label in self.cleaned_data["touristic_labels"]:
                    Labelling.objects.get_or_create(
                        activity=self.instance, touristic_label=label
                    )

            self.instance.update_main_labelling()
            self.instance.save()

        return self.instance


class ActivityAdminForm(ActivityBaseForm):
    pass
