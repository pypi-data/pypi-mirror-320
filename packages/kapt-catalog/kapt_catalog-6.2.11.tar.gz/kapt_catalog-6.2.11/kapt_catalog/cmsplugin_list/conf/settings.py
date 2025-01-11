# Third party
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


# The default order in which the results are displayed. Note that this order
# can be altered according to the options of the cmsplugin list instance.
RESULTS_ORDER_BY = getattr(
    settings, "CMSPLUGINLIST_RESULTS_ORDER_BY", ["translations__name"]
)

# A list of css classes that will be used to customize selections templates
# outputs.
CSS_CLASSES = getattr(settings, "CMSPLUGINLIST_CSS_CLASSES", (("", _("None")),))

# The list of templates that will be used to render selections.
TEMPLATES = getattr(settings, "CMSPLUGINLIST_TEMPLATES", None)
if not TEMPLATES:
    raise ImproperlyConfigured("CMSPLUGINLIST_TEMPLATES must be defined")

# Force the results of a selection to be filtered by the distance
# to a single geographical point.
LATITUDE = getattr(settings, "CMSPLUGINLIST_ORDER_BY_LATITUDE", None)
LONGITUDE = getattr(settings, "CMSPLUGINLIST_ORDER_BY_LONGITUDE", None)
SEARCH_RADIUS = getattr(settings, "CMSPLUGINLIST_SEARCH_RADIUS", 10000)

# Cache the results for 10 mins by default
CACHE_DURATION = getattr(settings, "CMSPLUGINLIST_CACHE_DURATION", 600)

# Cache random results for 30 mins by default.
# Set this value to 0 to disable caching of random results
RANDOM_SORTING_CACHE_DURATION = getattr(
    settings, "CMSPLUGINLIST_RANDOM_SORTING_CACHE_DURATION", 1800
)

NON_POLYMORPHIC = getattr(settings, "CMSPLUGINLIST_NON_POLYMORPHIC", False)
SELECT_RELATED = getattr(settings, "CMSPLUGINLIST_SELECT_RELATED", ["structure"])
PREFETCH_RELATED = getattr(settings, "CMSPLUGINLIST_PREFETCH_RELATED", ["translations"])


# The number of seconds the list of event activities ordered by dates
# should be stored in the cache
OPENING_DATE_SORTING_CACHE_DURATION = getattr(
    settings, "CMSPLUGINLIST_OPENING_DATE_SORTING_CACHE_DURATION", 60 * 60
)

# A list of Python paths to forms that will be used to define which
# kind of filtering we want to attach to the plugin instance.
FILTER_FORMS = getattr(settings, "CMSPLUGINLIST_FILTER_FORMS", [])

# A list of Python paths to context processors (simple functions that take a context
# dictionary as unique parameter) that will be used to inject additional data into the
# context used to render the plugin instance.
CONTEXT_PROCESSORS = getattr(
    settings, "CMSPLUGINLIST_CONTEXT_PROCESSORS", (("", _("None")),)
)

# The default context processor to apply when none are selected
DEFAULT_CONTEXT_PROCESSOR = getattr(
    settings, "CMSPLUGINLIST_DEFAULT_CONTEXT_PROCESSOR", None
)

# The list of filters that can be used during filtering operations.
# Note that these filters are always called, but you can use the provided arguments to process the queryset.
# For example by checking a value in `parameters` or in `instance.get_context_processor_list()`.
# Each item of this list must be the full python path to filter functions.
# Each filter function must be defined as follow:
# ```py
# filter(qs, parameters, instance)
# ```
#
# Where `qs` is the queryset to filter, `parameters` is a list of GET parameters
# and `instance` is the plugin config instance.
# Filter functions are dynamically loaded in the order they were declared in the
# CMSPLUGINLIST_FILTERS list.
DEFAULT_FILTERS = (
    "kapt_catalog.cmsplugin_list.cmspluginlist_filters.geonameid",
    "kapt_catalog.cmsplugin_list.cmspluginlist_filters.free_only",
)
FILTERS = getattr(settings, "CMSPLUGINLIST_FILTERS", DEFAULT_FILTERS)

DEFAULT_CONFIG = {
    "results_per_page": getattr(
        settings, "CMSPLUGINLIST_RESULTS_PER_PAGE", 10
    ),  # Backward compatibility
    "random_sorting": False,
    "opening_date_sorting": False,
    "registration_sorting": False,
    "registration_and_area_sorting": False,
    "bookable_sorting": False,
}
USER_CONFIG = getattr(settings, "CMSPLUGINLIST_DEFAULT_CONFIG", {})
DEFAULT_CONFIG.update(USER_CONFIG)


PLUGIN_NAME = getattr(settings, "CMSPLUGINLIST_PLUGIN_NAME", _("APIDAE Selection"))

CUSTOM_ACTIVITY_DATA_PREFETCH = getattr(
    settings, "CMSPLUGINLIST_CUSTOM_ACTIVITY_DATA_PREFETCH", []
)

ENABLE_SELECT2 = getattr(settings, "CMSPLUGINLIST_USE_SELECT2", False)
SELECT2_ENABLED = ENABLE_SELECT2 and "django_select2" in settings.INSTALLED_APPS
