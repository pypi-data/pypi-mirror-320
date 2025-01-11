# Standard Library
from importlib import import_module
import pickle
import urllib.parse

# Third party
from cms.constants import EXPIRE_NOW
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.translation import get_language, ugettext_lazy as _
from kapt_utils.utils.db import order_by_ids
from taggit.models import TaggedItem

# Local application / specific library imports
from .conf import settings
from .forms import ListPluginForm
from .models import ListPluginConf
from kapt_catalog.models import Activity, Structure, StructureReference
from kapt_catalog.utils.functions import (
    retrieve_address_of_activity_qs,
    retrieve_main_photos_of_activity_qs,
)


def handle_ids_based_sorting(request, page, activity_list, ids_key, ids_list):
    if page is None:
        request.session[ids_key] = ids_list
        # It seems that pickle breaks the order of a list (pickle is used by the Session Backend to
        # serialize data) when calling pickle.dumps(). Very weard!
        activity_list = order_by_ids(
            activity_list,
            pickle.loads(pickle.dumps(ids_list)),
            id_field="kapt_catalog_activity.id",
        )
    else:
        ids_list_session = request.session.get(ids_key, None)
        if ids_list_session:
            activity_list = order_by_ids(
                activity_list, ids_list_session, id_field="kapt_catalog_activity.id"
            )
        else:
            request.session[ids_key] = ids_list
            activity_list = order_by_ids(
                activity_list,
                pickle.loads(pickle.dumps(ids_list)),
                id_field="kapt_catalog_activity.id",
            )

    return activity_list


class ListPlugin(CMSPluginBase):
    model = ListPluginConf
    name = settings.PLUGIN_NAME
    render_template = True
    form = ListPluginForm
    exclude_if_no_choice = [
        "template",
        "css_class",
    ]  # Do not display these field if there is only one choice to choose from
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "tag_name",
                    "activities",
                    "results_per_page",
                    "only_translated",
                )
            },
        ),
        (
            _("Sorting"),
            {
                "classes": ("collapse",),
                "fields": (
                    "random_sorting",
                    "opening_date_sorting",
                    "registration_sorting",
                    "registration_and_area_sorting",
                    "bookable_sorting",
                ),
            },
        ),
    )

    cache = True

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        fields = [
            "only_aspect",
            "template",
            "css_class",
            "filter_form",
            "context_processor",
        ]
        fields_to_display = []

        for field_name in fields:
            field = self.model._meta.get_field(field_name)
            if (field_name in self.exclude_if_no_choice and len(field.choices) > 1) or (
                field_name not in self.exclude_if_no_choice and len(field.choices) > 0
            ):
                fields_to_display.append(field_name)

        if len(fields) > 0:
            fieldsets += (
                (
                    _("Advanced"),
                    {"classes": ("collapse",), "fields": fields_to_display},
                ),
            )

        return fieldsets

    def _import_from_module(self, ppath):
        module_path, name = ppath.rsplit(".", 1)
        module = import_module(module_path)

        if hasattr(module, name):
            return getattr(module, name)
        else:
            raise ImproperlyConfigured(
                "The '{}' module has no '{}' attribute".format(module, name)
            )

    def get_cache_expiration(self, request, instance, placeholder):
        # A bug in django-cms prevents distinction of paginated results in cache
        # Effect: cache return same results for different page=N query string
        # Solution: use the last commit of git://github.com/pierreben/django-cms.git, branch release/3.4.x
        if instance.filter_form or instance.get_random_sorting():
            return EXPIRE_NOW
        else:
            return settings.CACHE_DURATION

    def get_filters_form(self, request, instance, items):
        formBaseClasses = tuple(map(self._import_from_module, instance.filter_form))
        FilterFormClass = type(
            "FilterFormClass",
            formBaseClasses,
            {
                "request": request,
                "items": items,
                "list_plugin_instance": instance,
            },  # Pass the request, instance and the items to the form class as class attribute instead of in kwargs because FilterFormClass is a single class inheriting from formBaseClasses and it's the more relevant way to pass these args to all of the child classes (see https://www.programiz.com/python-programming/methods/built-in/type and https://stackoverflow.com/questions/22609272/python-typename-bases-dict#:~:text=__bases__%20is%20a,dynamically%20generate%20classes%20at%20runtime.)
            # So in the sub classes (formBaseClasses), these args are accessible via self.request, self.items and self.list_plugin_instance
        )
        return FilterFormClass(
            request.GET,
            items=items,  # Keep the request GET and items as kwargs for retro compatibility purpose but this should not be used anymore
        )

    def get_context_processors(self, context_processors):
        return map(self._import_from_module, context_processors)

    def render(self, context, instance, placeholder):
        context["conf"] = instance
        request = context["request"]
        page = request.GET.get("page")
        self.render_template = "cmsplugin_list/{}".format(instance.template)

        if instance.activities.count() == 0:
            tag_names = instance.get_tags_names()

            content_type = ContentType.objects.get_for_model(StructureReference)

            references_list = list(
                TaggedItem.objects.filter(
                    tag__name__in=tag_names, content_type_id=content_type.id
                ).values_list("object_id", flat=True)
            )
        else:
            references_list = [
                activity.structure.reference.pk
                for activity in instance.activities.all()
            ]

        order_by_list = []
        if instance.get_registration_and_area_sorting():
            order_by_list += [
                "-reference__profile__is_registered",
                "-reference__profile__on_area",
            ]

        elif instance.get_registration_sorting():
            order_by_list += ["-reference__profile__is_registered"]

        elif instance.get_bookable_sorting():
            order_by_list += ["booking_url"]

        order_by_list += settings.RESULTS_ORDER_BY

        # Only valid structures are fetched
        structure_list = list(
            Structure.objects.filter(
                Q(reference__pk__in=references_list),
                Q(reference__is_active=True),
                (
                    Q(validity_period__valid_from__lte=timezone.now())
                    | Q(validity_period__valid_from__isnull=True)
                ),
                Q(validity_period__valid_until__gte=timezone.now()),
            ).values_list("id", flat=True)
        )

        if instance.only_aspect == 0:
            activity_manager = Activity.no_aspects
            aspect_filter = {}
        else:
            activity_manager = Activity.objects
            aspect_filter = {"aspect": instance.only_aspect}

        if settings.NON_POLYMORPHIC:
            activity_list = activity_manager.non_polymorphic()
        else:
            activity_list = activity_manager.all()

        if instance.only_translated:
            activity_list = activity_list.translated(request.LANGUAGE_CODE).distinct()
        else:
            # This queryset can be bogus when there are more than one fallback languages
            # See https://gitlab.com/kapt/doc/general/-/issues/293
            activity_list = activity_list.active_translations().distinct()

        activity_list = (
            activity_list.filter(structure__pk__in=structure_list, **aspect_filter)
            .select_related(*settings.SELECT_RELATED)
            .prefetch_related(*settings.PREFETCH_RELATED)
        )

        # Handles filters if the 'search engine' mode is enabled
        if instance.filter_form:
            # First, append the form to the context
            context["form"] = self.get_filters_form(
                request=request, instance=instance, items=activity_list
            )
            context["form"].is_valid()

            # Then, filters
            parameters = request.GET.copy()
            for search_filter in settings.FILTERS:
                try:
                    activity_list = self._import_from_module(search_filter)(
                        activity_list, parameters, instance
                    )
                except TypeError:
                    # For retro compatibility purpose
                    activity_list = self._import_from_module(search_filter)(
                        activity_list, parameters
                    )
                except Exception:
                    pass

        # Handle LATITUDE and LONGITUDE sorting
        if (
            settings.LATITUDE
            and settings.LONGITUDE
            and not instance.get_random_sorting()
        ):
            distance = """
                SELECT 6371 * ACOS(
                    COS(PI() * kapt_geo_address.latitude/180)
                    * COS(PI() * %s/180)
                    * COS(PI() * kapt_geo_address.longitude/180)
                    * COS(PI() * %s/180)
                    + COS(PI() * kapt_geo_address.latitude/180)
                    * SIN(PI() * kapt_geo_address.longitude/180)
                    * COS(PI() * %s/180)
                    * SIN(PI() * %s/180)
                    + SIN(PI() * kapt_geo_address.latitude/180)
                    * SIN(PI() * %s/180)
                )
            """
            activity_list = activity_list.extra(
                select={
                    "distance": "{} FROM kapt_geo_address WHERE (kapt_geo_address.id = address_id)".format(
                        distance
                    )
                },
                select_params=[
                    settings.LATITUDE,
                    settings.LONGITUDE,
                    settings.LATITUDE,
                    settings.LONGITUDE,
                    settings.LATITUDE,
                ],
                where=(
                    "kapt_catalog_structure.id = kapt_catalog_activity.structure_id",
                    "kapt_geo_address.id = kapt_catalog_structure.address_id",
                    "{} <= %s".format(distance),
                ),
                params=[
                    settings.LATITUDE,
                    settings.LONGITUDE,
                    settings.LATITUDE,
                    settings.LONGITUDE,
                    settings.LATITUDE,
                    settings.SEARCH_RADIUS,
                ],
                tables=["kapt_catalog_structure", "kapt_geo_address"],
            )
            order_by_list = ["distance"] + order_by_list

        elif instance.get_opening_date_sorting():
            cache_key = "date_sorting_{}_{}_{}".format(
                instance.tag_name, get_language(), urlencode(request.GET.copy())
            )
            cached_activity_list = cache.get(cache_key, None)

            if not cached_activity_list:
                now_dt = timezone.now().date()

                # Keep only the useful events and sort them by date
                activity_list = filter(
                    lambda item: item.next_validity_date is not None
                    and item.next_validity_date >= now_dt,
                    activity_list,
                )
                activity_list = sorted(
                    activity_list, key=lambda item: item.next_validity_date
                )

                cache.set(
                    cache_key,
                    activity_list,
                    settings.OPENING_DATE_SORTING_CACHE_DURATION,
                )
            else:
                activity_list = cached_activity_list

        # Handle random sorting
        elif instance.get_random_sorting():
            get_data = request.GET.copy()
            get_data.pop("page", None)

            ids_key = "random_{}_{}_{}".format(
                instance.tag_name, get_language(), urlencode(get_data)
            )
            activity_list = activity_list.order_by("?")
            order_by_list = []

            if instance.get_registration_and_area_sorting():
                on_area_registered_ids = activity_list.filter(
                    reference__profile__is_registered=True,
                    reference__profile__on_area=True,
                ).values_list("id", flat=True)
                registered_ids = activity_list.filter(
                    reference__profile__is_registered=True,
                    reference__profile__on_area=False,
                ).values_list("id", flat=True)
                other_ids = activity_list.filter(
                    reference__profile__is_registered=False
                ).values_list("id", flat=True)
                ids_list = (
                    list(on_area_registered_ids)
                    + list(registered_ids)
                    + list(other_ids)
                )

            elif instance.get_registration_sorting():
                registered_ids = activity_list.filter(
                    reference__profile__is_registered=True
                ).values_list("id", flat=True)
                other_ids = activity_list.filter(
                    reference__profile__is_registered=False
                ).values_list("id", flat=True)
                ids_list = list(registered_ids) + list(other_ids)

            elif instance.get_bookable_sorting():
                bookable_ids = activity_list.filter(
                    structure__booking_url__isnull=False
                ).values_list("id", flat=True)
                other_ids = activity_list.filter(
                    structure__booking_url__isnull=True
                ).values_list("id", flat=True)
                ids_list = list(bookable_ids) + list(other_ids)

            else:
                ids_list = list(activity_list.values_list("id", flat=True))

            if len(ids_list) > 0:
                activity_list = handle_ids_based_sorting(
                    request, page, activity_list, ids_key, ids_list
                )

        # Apply ordering
        if isinstance(activity_list, QuerySet) and len(order_by_list) > 0:
            activity_list = activity_list.order_by(*order_by_list).distinct()

        paginator = Paginator(activity_list, instance.get_results_per_page())

        ancestors = context.get("ancestors", None)
        if ancestors:
            if len(request.GET) > 0:
                ancestors[-1].url = "{}?{}".format(
                    ancestors[-1].url, urlencode(request.GET)
                )
            request.session["breadcrumb"] = ancestors
            request.session["parent"] = ancestors[-1]

        try:
            paginated_activities = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paginated_activities = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paginated_activities = paginator.page(paginator.num_pages)

        structure_ids = [a.structure_id for a in paginated_activities]
        retrieve_main_photos_of_activity_qs(paginated_activities, structure_ids)
        retrieve_address_of_activity_qs(paginated_activities, structure_ids)

        for prefetch_function in settings.CUSTOM_ACTIVITY_DATA_PREFETCH:
            self._import_from_module(prefetch_function)(paginated_activities)

        context["instance"] = instance
        # keep fo retro compatibility purpose
        context["activities"] = paginated_activities
        context["paginated_activities"] = paginated_activities
        context["all_activities"] = activity_list
        context["activity_ct_id"] = ContentType.objects.get_for_model(Activity).id

        # Save the path for potential filter operations
        path = request.path
        querystring = request.META.get("QUERY_STRING", "")
        query_dict = dict(urllib.parse.parse_qsl(querystring))
        if "page" in query_dict:
            del query_dict["page"]
        querystring = urllib.parse.urlencode(query_dict)

        path_without_query = path
        if querystring:
            path = "{}?{}&".format(path, querystring)
            path_without_query = path
        else:
            path_without_query = path
            path = "{}?".format(path)

        context["path"] = path
        context["path_without_query"] = path_without_query

        # Apply default
        if (
            settings.DEFAULT_CONTEXT_PROCESSOR is not None
            and instance.context_processor is not None
            and settings.DEFAULT_CONTEXT_PROCESSOR not in instance.context_processor
        ):
            instance.context_processor.append(settings.DEFAULT_CONTEXT_PROCESSOR)

        if instance.context_processor:
            context_processors = self.get_context_processors(instance.context_processor)
            for context_processor in context_processors:
                context = context_processor(context)

        context["is_wishlist_installed"] = apps.is_installed("kapt_wishlist")

        return context


plugin_pool.register_plugin(ListPlugin)
