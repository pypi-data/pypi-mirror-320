# Third party
from django.core.management.base import BaseCommand
from django.utils.translation import activate

# Local application / specific library imports
from kapt_catalog.models import Activity


class Command(BaseCommand):
    help = "Reset slugs after bug fix"

    def handle(self, *args, **options):
        self.stdout.write("###################")
        self.stdout.write("# Start")
        self.stdout.write("###################")

        activate("fr")

        activities = Activity.objects.all()
        for activity in activities:
            activity.slug = ""
            activity.save(generate_slug=True)
            self.stdout.write("Slug for {} is {}".format(activity.name, activity.slug))

        self.stdout.write("End")
