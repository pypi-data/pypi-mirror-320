from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class KaptCatalogRegistryConfig(AppConfig):
    label = "kapt_catalog"
    name = "kapt_catalog"
    verbose_name = _("Kapt Catalog")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):  # pragma: no cover
        from . import receivers  # noqa
