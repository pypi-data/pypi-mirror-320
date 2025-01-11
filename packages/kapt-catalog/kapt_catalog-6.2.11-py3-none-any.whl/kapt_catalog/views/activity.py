# Standard library imports

# Third party
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy
from django.forms.forms import NON_FIELD_ERRORS
from django.http import Http404
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from extra_views import ModelFormSetView
from kapt_gallery.forms import PhotoForm, PhotoFormSet, PhotoFormSetHelper
from kapt_gallery.models import Gallery, Photo

# Local application / specific library imports
from kapt_catalog.forms.activities.accommodation import (
    BnBActivityBedFormSet,
    RentalActivityBedFormSet,
    RoomForm,
)
from kapt_catalog.models.activities import Activity
from kapt_catalog.models.activities.accommodation import (
    AccommodationActivity,
    Bed,
    Room,
)
from kapt_catalog.models.characteristic import Characteristic
from kapt_catalog.views import DashboardContextMixin


# -- [ Temporary comment ] -- Generic views
# -- ----------------------------------------------------
class PolymorphicView(View):
    # TODO: this view only works for Activity subclasses (because of the default value when no parameters are passed), it should be more generic
    """
    Handles a GET parameter which sould contain a content type ID and store this value
    to slef.model attribute.
    If the parameter is not found, fall back to the Activity content type ID.
    """

    def dispatch(self, request, *args, **kwargs):
        default_ct = ContentType.objects.get(app_label="kapt_catalog", model="activity")
        child_type_id = int(self.request.GET.get("type", default_ct.id))

        try:
            ct = ContentType.objects.get_for_id(child_type_id)
        except ContentType.DoesNotExist as e:
            raise Http404(e)  # Handle invalid GET parameters

        self.model = ct.model_class()
        if not self.model:
            raise Http404(
                "No model found for '{}.{}'.".format(*ct.natural_key())
            )  # Handle model deletion

        return super().dispatch(request, *args, **kwargs)


class ActivityCreateView(CreateView, PolymorphicView, DashboardContextMixin):
    template_name = "kapt_catalog/activity_form.html"

    initial = {
        "reference": 0,
        "visibility": Characteristic.objects.get(
            identifier="visibility"
        ).get_active_descendants(),  # All visibilities checked by default
    }

    def get_initial(self, *args, **kwargs):
        initial = super().get_initial(*args, **kwargs)
        initial.update(structure=self.kwargs["structure_pk"])
        return initial

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)

        context["model_name"] = self.model._meta.verbose_name.title()
        context["ct"] = ContentType.objects.get_for_model(self.model).pk
        ct = ContentType.objects.get_for_model(self.model)
        parent_model_class = ct.model_class().__bases__[0]
        parent_ct = ContentType.objects.get_for_model(parent_model_class)
        if parent_ct.pk == ContentType.objects.get_for_model(Activity).pk:
            context["has_no_parent_ct"] = True
        context["steps"] = self.model.STEPS

        return context

    def get_form_class(self):
        return self.model().get_form_class()

    def get_success_url(self):
        return "{}?success=true".format(
            reverse_lazy(
                "dashboard-activity-edit",
                kwargs={
                    "pk": self.object.id,
                    "structure_pk": self.kwargs["structure_pk"],
                },
            )
        )


class ActivityEditView(UpdateView, PolymorphicView, DashboardContextMixin):
    template_name = "kapt_catalog/activity_update_form.html"

    def get_form_class(self):
        return self.object.get_form_class()

    def get_success_url(self):
        return "{}?success=true".format(
            reverse_lazy(
                "dashboard-activity-edit",
                kwargs={
                    "pk": self.object.id,
                    "structure_pk": self.kwargs["structure_pk"],
                },
            )
        )


class ActivityEditCharacteristicView(
    UpdateView, PolymorphicView, DashboardContextMixin
):
    template_name = "kapt_catalog/activity_update_form.html"

    def get_form_class(self):
        return self.object.get_form_class(step="characteristic")

    def get_success_url(self):
        return "{}?success=true".format(
            reverse_lazy(
                "dashboard-activity-characteristic-edit",
                kwargs={
                    "pk": self.object.id,
                    "structure_pk": self.kwargs["structure_pk"],
                },
            )
        )


class ActivityEditPhotoView(ModelFormSetView, DashboardContextMixin):
    model = Photo
    template_name = "kapt_catalog/activity_photo_update_form.html"
    form_class = PhotoForm
    formset_class = PhotoFormSet
    extra = 4
    max_num = 4
    can_delete = True

    def dispatch(self, *args, **kwargs):
        """
        Create a gallery for this activity if it does not exist.
        """
        response = super().dispatch(*args, **kwargs)

        activity = Activity.objects.get(pk=self.kwargs["pk"])

        if not activity.gallery:
            # Create a gallery for this activity
            gallery = Gallery.objects.create(
                name="Activity #{}".format(activity.pk),
                slugname="activity-{}".format(activity.pk),
            )
            activity.gallery = gallery
            activity.save()

        return response

    def get_extra_form_kwargs(self):
        gallery = Activity.objects.get(pk=self.kwargs["pk"]).gallery
        return {"gallery": gallery}

    def get_queryset(self):
        activity = Activity.objects.get(pk=self.kwargs["pk"])

        if not activity.gallery:
            return Photo.objects.none()
        else:
            return activity.gallery.photo_set.all().order_by("number")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["object"] = Activity.objects.get(pk=self.kwargs["pk"])

        if "structure_pk" in self.kwargs:
            context["structure_pk"] = self.kwargs["structure_pk"]

            helper = PhotoFormSetHelper()
            context["helper"] = helper

        return context

    def get_success_url(self):
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        return "{}?success=true".format(
            reverse_lazy(
                "dashboard-activity-photo-edit",
                kwargs={"pk": activity.id, "structure_pk": self.kwargs["structure_pk"]},
            )
        )


class ActivityListView(ListView, PolymorphicView, DashboardContextMixin):
    def get_queryset(self):
        queryset = Activity.objects.instance_of(self.model)

        if "structure_pk" in self.kwargs:
            queryset = queryset.filter(structure_id=self.kwargs["structure_pk"])

        return queryset

    def get_template_names(self):
        accommodation_ct = ContentType.objects.get(model=AccommodationActivity.__name__)
        model_ct = ContentType.objects.get(model=self.model.__name__)
        if model_ct == accommodation_ct:
            return ["kapt_catalog/activity_accommodation_list.html"]
        return ["kapt_catalog/activity_list.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "child_type_choices": self.model.get_child_type_choices(),
                "model_name": self.model._meta.verbose_name,
                "model_ct": ContentType.objects.get_for_model(self.model).id,
            }
        )

        return context


class ActivityDetailView(DetailView, PolymorphicView):
    template_name = "kapt_catalog/activity_detail.html"


class ActivityDeleteView(DeleteView):
    model = Activity
    template_name = "kapt_catalog/delete_confirmation.html"
    success_url = reverse_lazy("activity-list")


# -- [ Temporary comment ] -- Specific views
# -- ----------------------------------------------------


class BnBActivityEditCharacteristicView(
    UpdateView, PolymorphicView, DashboardContextMixin
):
    template_name = "kapt_catalog/activity_bnb_edit_characteristic_form.html"

    def get_form_class(self):
        return self.object.get_form_class(step="characteristic")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.capacity >= self.object.maximum_capacity:
            context["max_capacity_reached"] = True

        if self.request.method == "POST":
            context["bed_formset"] = BnBActivityBedFormSet(
                data=self.request.POST, accommodation_activity=self.object
            )
        else:
            context["bed_formset"] = BnBActivityBedFormSet(
                queryset=Bed.objects.filter(room__accommodation=self.object),
                accommodation_activity=self.object,
            )
        return context

    def form_valid(self, form):
        # TODO: bad http citizen: a valid post should do a http redirect, not a render
        context = self.get_context_data()
        bed_formset = context["bed_formset"]
        if bed_formset.is_valid():
            bed_formset.save()
        else:
            form._errors[NON_FIELD_ERRORS] = bed_formset._non_form_errors
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return "{}?success=true".format(
            reverse_lazy(
                "dashboard-bnb-activity-characteristic-edit",
                kwargs={
                    "pk": self.object.id,
                    "structure_pk": self.kwargs["structure_pk"],
                },
            )
        )


class RentalActivityRoomsListView(DetailView, PolymorphicView, DashboardContextMixin):
    template_name = "kapt_catalog/activity_rental_rooms_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Get the rooms associated to this rental activity
        context["room_list"] = Room.objects.filter(accommodation=self.object)
        context["capacity"] = self.object.capacity
        if self.object.capacity >= self.object.maximum_capacity:
            context["max_capacity_reached"] = True

        return context


class RoomCreateView(CreateView, PolymorphicView, DashboardContextMixin):
    form_class = RoomForm
    template_name = "kapt_catalog/room_form.html"

    initial = {"capacity": 0}

    def get(self, request, *args, **kwargs):
        if "structure_pk" in kwargs:
            self.initial["accommodation"] = kwargs["pk"]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        context["object"] = activity
        if self.request.method == "POST":
            context["bed_formset"] = RentalActivityBedFormSet(
                data=self.request.POST, accommodation_activity=activity
            )
        else:
            context["bed_formset"] = RentalActivityBedFormSet(
                queryset=Bed.objects.filter(room__pk=None),
                accommodation_activity=activity,
            )
        return context

    def form_valid(self, form):
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        if super().form_valid(form):
            obj = form.save()
            bed_formset = RentalActivityBedFormSet(
                data=self.request.POST, accommodation_activity=activity, room=obj
            )
            if bed_formset.is_valid():
                bed_formset.save()
            else:
                obj.delete()
                form._errors[NON_FIELD_ERRORS] = bed_formset._non_form_errors
                return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        return "{}?alert=success".format(
            reverse_lazy(
                "dashboard-rental-activity-rooms-list",
                kwargs={"pk": activity.pk, "structure_pk": self.kwargs["structure_pk"]},
            )
        )


class RoomEditView(UpdateView, PolymorphicView, DashboardContextMixin):
    model = Room
    form_class = RoomForm
    template_name = "kapt_catalog/room_update_form.html"

    def get_object(self, queryset=None):
        return Room.objects.get(pk=self.kwargs["room_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        context["activity"] = activity
        if activity.capacity >= activity.maximum_capacity:
            context["max_capacity_reached"] = True

        if self.request.method == "POST":
            context["bed_formset"] = RentalActivityBedFormSet(
                data=self.request.POST,
                accommodation_activity=activity,
                room=self.object,
            )
        else:
            context["bed_formset"] = RentalActivityBedFormSet(
                queryset=Bed.objects.filter(
                    room=self.object, room__accommodation=activity
                ),
                accommodation_activity=activity,
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        bed_formset = context["bed_formset"]
        if bed_formset.is_valid():
            bed_formset.save()
        else:
            form._errors[NON_FIELD_ERRORS] = bed_formset._non_form_errors
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        return "{}?success=true".format(
            reverse_lazy(
                "dashboard-rental-activity-rooms-list",
                kwargs={"pk": activity.pk, "structure_pk": self.kwargs["structure_pk"]},
            )
        )


class RoomDeleteView(DeleteView):
    model = Room
    template_name = "kapt_catalog/delete_confirmation.html"
    pk_url_kwarg = "room_pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        context["structure_pk"] = activity.structure.pk
        return context

    def get_success_url(self):
        activity = Activity.objects.get(pk=self.kwargs["pk"])
        activity.compute_capacity()
        activity.save()
        return "{}?success=true".format(
            reverse_lazy(
                "dashboard-rental-activity-rooms-list",
                kwargs={"pk": activity.pk, "structure_pk": self.kwargs["structure_pk"]},
            )
        )
