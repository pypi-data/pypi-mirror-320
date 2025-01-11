# Third party
from django.core.management.base import BaseCommand

# Local application / specific library imports
from kapt_catalog.cmsplugin_list.models import ListPluginConf


class Command(BaseCommand):
    help = "Empty results_per_page field on cmsplugin_list, if its value is 10, to use the default value"

    def handle(self, *args, **options):
        self.stdout.write("###################")
        self.stdout.write("# Start")
        self.stdout.write("###################")

        plugins = ListPluginConf.objects.filter(results_per_page=10)
        plugins.update(results_per_page=None)

        self.stdout.write(
            "Found {} plugins with results_per_page == 10".format(plugins.count())
        )

        self.stdout.write("End")
