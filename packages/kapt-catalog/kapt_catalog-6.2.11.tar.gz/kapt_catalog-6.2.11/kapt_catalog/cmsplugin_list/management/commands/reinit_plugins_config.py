# Third party
from django.core.management.base import BaseCommand

# Local application / specific library imports
from kapt_catalog.cmsplugin_list.models import ListPluginConf


class Command(BaseCommand):
    help = "Reinitialize config of existing cmsplugin_list"

    def handle(self, *args, **options):
        self.stdout.write("###################")
        self.stdout.write("# Start")
        self.stdout.write("###################")

        plugins = ListPluginConf.objects.all()

        for plugin in plugins:
            plugin.results_per_page = None
            plugin.random_sorting = None
            plugin.opening_date_sorting = None
            plugin.registration_sorting = None
            plugin.registration_and_area_sorting = None
            plugin.bookable_sorting = None
            plugin.save()

        self.stdout.write("Reinitialized config on {} plugins".format(plugins.count()))

        self.stdout.write("End")
