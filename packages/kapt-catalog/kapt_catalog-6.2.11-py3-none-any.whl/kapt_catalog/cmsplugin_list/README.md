# Kapt-catalog cmsplugin-list

## Setup

1. Install and setup kapt-catalog
1. Install and setup kapt-site
1. Add in `INSTALLED_APPS`:
   ```python
   "kapt_catalog.cmsplugin_list",
   ```
1. Generate translated fields
   ```bash
   python manage.py sync_translation_fields --noinput
   ```
1. Migrate database
   ```bash
   python manage.py migrate
   ```

### Required settings

You must define a constant in your settings:
```py
CMSPLUGINLIST_TEMPLATES = (
  ("template.html", "label"),
)
```
`template.html` must be in a `templates/cmsplugin_list/` folder.

### Other settings

#### `CMSPLUGINLIST_RESULTS_ORDER_BY = ["translations__name"]`

The default order in which the results are displayed. Note that this order
can be altered according to the options of the cmsplugin list instance.

#### `CMSPLUGINLIST_CSS_CLASSES = (("", _("None")),)`

A list of css classes that will be used to customize selections templates
outputs.

#### `CMSPLUGINLIST_ORDER_BY_LATITUDE = None` and `CMSPLUGINLIST_ORDER_BY_LONGITUDE = None`

Force the results of a selection to be filtered by the distance
to a single geographical point.

#### `CMSPLUGINLIST_SEARCH_RADIUS = 10000`

The radius for the search by distance filter. If `CMSPLUGINLIST_ORDER_BY_LATITUDE` and `CMSPLUGINLIST_ORDER_BY_LONGITUDE` are defined.

#### `CMSPLUGINLIST_CACHE_DURATION = 600`

Cache the results for 10 mins by default

#### `CMSPLUGINLIST_RANDOM_SORTING_CACHE_DURATION = 1800`

Cache random results for 30 mins by default.
Set this value to 0 to disable caching of random results

#### `CMSPLUGINLIST_NON_POLYMORPHIC = False`

Deactivate polymorphic querysets.

#### `CMSPLUGINLIST_SELECT_RELATED = ["structure"]`

Define the related fields selected on the queryset.

#### `CMSPLUGINLIST_PREFETCH_RELATED = ["translations"]`

Define the related fields prefetched on the queryset.

#### `CMSPLUGINLIST_OPENING_DATE_SORTING_CACHE_DURATION = 60 * 60`

The number of seconds the list of event activities ordered by dates
should be stored in the cache

#### `CMSPLUGINLIST_FILTER_FORMS = []`

A list of tuples to forms classes that will be used to define which
kind of filtering we want to attach to the plugin instance.

For example:
```py
[
  ("path.to.my.filter.form.Class", "Displayed name"),
]
```

#### `CMSPLUGINLIST_CONTEXT_PROCESSORS = (("", _("None")),)`

A list of Python paths to context processors (simple functions that take a context
dictionary as unique parameter) that will be used to inject additional data into the
context used to render the plugin instance.

#### `CMSPLUGINLIST_DEFAULT_CONTEXT_PROCESSOR = None`

The default context processor to apply when none are selected

#### `CMSPLUGINLIST_FILTERS`
Default value:
```py
(
    "kapt_catalog.cmsplugin_list.cmspluginlist_filters.geonameid",
    "kapt_catalog.cmsplugin_list.cmspluginlist_filters.free_only",
)
```

The list of filters that can be used during filtering operations.
Note that all these filters are called but only when a FILTER_FORM is enabled on the plugin.
You can use the provided arguments to process the queryset: for example by checking a value in `parameters` or in `instance.get_context_processor_list()`.
Each item of this list must be the full python path to filter functions.
Each filter function must be defined as follow:
```py
filter(qs, parameters, instance)
```

Where `qs` is the queryset to filter, `parameters` is a list of GET parameters
and `instance` is the plugin config instance.
Filter functions are dynamically loaded in the order they were declared in the
`CMSPLUGINLIST_FILTERS` list.

#### `CMSPLUGINLIST_DEFAULT_CONFIG = {}`

The default values for the config of the plugins.

Default value:
```py
{
    "results_per_page": getattr(
        settings, "CMSPLUGINLIST_RESULTS_PER_PAGE", 10
    ),  # Backward compatibility, do not use `CMSPLUGINLIST_RESULTS_PER_PAGE`
    "random_sorting": False,
    "opening_date_sorting": False,
    "registration_sorting": False,
    "registration_and_area_sorting": False,
    "bookable_sorting": False,
}
```

You can pass a dict with only the keys you want to override.

#### `CMSPLUGINLIST_PLUGIN_NAME = _("APIDAE Selection")`

The name displayed on the CMS admin.

#### `CMSPLUGINLIST_CUSTOM_ACTIVITY_DATA_PREFETCH = []`

A list of paths (strings) to functions which takes only one argument: the list of activities of the current displayed page

#### `CMSPLUGINLIST_USE_SELECT2 = False`

Enable Select2 on plugin admin form.

## Cache management

Django CMS does not handle query parameters in placeholder cache ([this issue on Github](https://github.com/django-cms/django-cms/issues/5565)).
The cache is disabled when at least one of these statement is true:

- a form is enabled on the plugin ([see code](https://gitlab.com/kapt/modules/kapt-catalog/-/blob/master/kapt_catalog/cmsplugin_list/cms_plugins.py#L145))
- random sorting is enabled ([see code](https://gitlab.com/kapt/modules/kapt-catalog/-/blob/master/kapt_catalog/cmsplugin_list/cms_plugins.py#L145))
- `CMSPLUGINLIST_CACHE_DURATION` is set to 0
