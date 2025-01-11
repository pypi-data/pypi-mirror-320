# Third party
from django.forms import models
from django.template.defaultfilters import yesno
from django.utils.translation import ugettext

# Local application / specific library imports
from .conf import settings
from .fields import ActivitySearchField
from .models import ListPluginConf


class ListPluginForm(models.ModelForm):
    if settings.SELECT2_ENABLED:
        activities = ActivitySearchField(
            label=ugettext("APIDAE objects"),
            required=False,
            placeholder=ugettext("Search APIDAE objects"),
        )
    else:
        activities = ActivitySearchField(
            label=ugettext("APIDAE objects"), required=False
        )

    class Meta:
        model = ListPluginConf
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        YESNO = ugettext("yes,no")

        self.fields["random_sorting"].help_text = ugettext("Defaults to: {}").format(
            yesno(settings.DEFAULT_CONFIG["random_sorting"], YESNO)
        )
        self.fields["opening_date_sorting"].help_text += " " + ugettext(
            "Defaults to: {}"
        ).format(yesno(settings.DEFAULT_CONFIG["opening_date_sorting"], YESNO))
        self.fields["registration_sorting"].help_text = ugettext(
            "Defaults to: {}"
        ).format(yesno(settings.DEFAULT_CONFIG["registration_sorting"], YESNO))
        self.fields["registration_and_area_sorting"].help_text = ugettext(
            "Defaults to: {}"
        ).format(yesno(settings.DEFAULT_CONFIG["registration_and_area_sorting"], YESNO))
        self.fields["bookable_sorting"].help_text = ugettext("Defaults to: {}").format(
            yesno(settings.DEFAULT_CONFIG["bookable_sorting"], YESNO)
        )

        if "template" in self.fields:
            self.fields["template"].choices = [
                (choice[0], ugettext(choice[1]))
                for choice in self.fields["template"].choices
            ]
        if "css_class" in self.fields:
            self.fields["css_class"].choices = [
                (choice[0], ugettext(choice[1]))
                for choice in self.fields["css_class"].choices
            ]
        if "filter_form" in self.fields:
            self.fields["filter_form"].choices = [
                (choice[0], ugettext(choice[1]))
                for choice in self.fields["filter_form"].choices
            ]
        if "context_processor" in self.fields:
            self.fields["context_processor"].choices = [
                (choice[0], ugettext(choice[1]))
                for choice in self.fields["context_processor"].choices
            ]
            if self.initial.get("context_processor", None) is None:
                self.initial["context_processor"] = [settings.DEFAULT_CONTEXT_PROCESSOR]

    def clean(self):
        cleaned_data = super().clean()
        tag_name = cleaned_data.get("tag_name")
        activities = cleaned_data.get("activities")

        if (tag_name is None or len(tag_name) == 0) and (
            activities is None or len(activities) == 0
        ):
            self._errors["activities"] = self._errors["tag_name"] = self.error_class(
                [ugettext("Either tag name or activities is required.")]
            )

        if tag_name and len(tag_name) > 0 and activities and len(activities) > 0:
            self._errors["activities"] = self._errors["tag_name"] = self.error_class(
                [ugettext("Fill only tag name or activities not both.")]
            )

        return cleaned_data
