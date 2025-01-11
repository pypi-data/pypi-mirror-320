# Third party
from django.core.management.base import BaseCommand

# Local application / specific library imports
from kapt_catalog.cmsplugin_list.conf.settings import DEFAULT_CONTEXT_PROCESSOR
from kapt_catalog.cmsplugin_list.models import ListPluginConf


class Command(BaseCommand):
    help = "Apply default context_processor to existing cmsplugin_list"

    def handle(self, *args, **options):
        self.stdout.write("###################")
        self.stdout.write("# Start")
        self.stdout.write("###################")

        plugins = ListPluginConf.objects.all()

        for plugin in plugins:
            new_processors = plugin.context_processor or []
            new_processors.append(DEFAULT_CONTEXT_PROCESSOR)
            plugin.context_processor = new_processors
            plugin.save()

        self.stdout.write(
            "Applied default procesor on {} plugins".format(plugins.count())
        )

        self.stdout.write("End")
