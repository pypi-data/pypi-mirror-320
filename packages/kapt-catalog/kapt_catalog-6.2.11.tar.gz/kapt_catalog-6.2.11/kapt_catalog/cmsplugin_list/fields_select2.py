# Third party
from django import forms
from django.db.models import Q
from django.utils import timezone
from django_select2.forms import ModelSelect2MultipleWidget

# Local application / specific library imports
from kapt_catalog.models import Activity


class Select2ActivitySearchFieldMixin:
    search_fields = [
        "translations__name__icontains",
        "structure__name__icontains",
        "reference__former_identifier__icontains",
    ]


class Select2ActivitySelectWidget(
    Select2ActivitySearchFieldMixin, ModelSelect2MultipleWidget
):
    def get_queryset(self):
        return Activity.objects.filter(
            (
                Q(structure__validity_period__valid_from__lte=timezone.now())
                | Q(structure__validity_period__valid_from__isnull=True)
            ),
            (
                Q(structure__validity_period__valid_until__gte=timezone.now())
                | Q(structure__validity_period__valid_until__isnull=True)
            ),
            structure__reference__is_active=True,
            is_active=True,
            is_public=True,
        )

    class Media:
        # django-select2 does not provide jQuery, but jQuery is already provided by the django's admin
        # But if we don't specify that our widget requires jQuery, it will eventually be loaded after select2'js
        js = (
            "admin/js/jquery.init.js",
            "admin/js/vendor/select2/select2.full.min.js",
        )


class Select2ActivitySearchField(forms.ModelMultipleChoiceField):
    widget = Select2ActivitySelectWidget()

    def __init__(self, *args, **kwargs):
        kwargs["queryset"] = self.widget.get_queryset()
        placeholder = kwargs.pop("placeholder")
        super().__init__(*args, **kwargs)
        self.widget.attrs["data-placeholder"] = placeholder
