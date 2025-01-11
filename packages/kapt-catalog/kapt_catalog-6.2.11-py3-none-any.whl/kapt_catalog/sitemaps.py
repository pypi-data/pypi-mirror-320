# Third party
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.utils.translation import activate, get_language

# Local application / specific library imports
from kapt_catalog.conf import settings as catalog_settings
from kapt_catalog.models import Activity


class ActivitySitemap(Sitemap):
    changefreq = catalog_settings.ACTIVITY_SITEMAP_CHANGEFREQ
    priority = 0.6

    def __init__(self, language=settings.LANGUAGE_CODE):
        self.language = language
        super().__init__()

    def items(self):
        return Activity.objects.filter(is_active=True, is_public=True)

    def lastmod(self, obj):
        return obj.modified_on

    def location(self, obj):
        curr_language = get_language()
        try:
            activate(self.language)
            url = catalog_settings.ACTIVITY_SITEMAP_ITEMS_LOCATION(obj)
        finally:
            activate(curr_language)
        return url
