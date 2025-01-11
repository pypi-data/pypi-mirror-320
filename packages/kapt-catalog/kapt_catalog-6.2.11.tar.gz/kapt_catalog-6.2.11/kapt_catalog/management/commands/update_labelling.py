from django.core.management.base import BaseCommand

# Local application / specific library imports
from kapt_catalog.models import Activity


class Command(BaseCommand):
    help = """
    Update default, main and prefectoral labelling attributes on all activities
    """

    def handle(self, *args, **options):
        self.stdout.write("Will update:")
        self.stdout.write("\t- default labelling")
        self.stdout.write("\t- main labelling")
        self.stdout.write("\t- prefectoral labelling")
        self.stdout.write("on all activities")

        activities = Activity.objects.all()
        counter = 0
        total = activities.count()
        for activity in activities:
            activity.update_default_labelling()
            activity.update_main_labelling()
            activity.update_prefectoral_labelling()

            activity.save()
            counter += 1
            self.stdout.write(f"\rUpdating {counter}/{total}...", ending="")
            self.stdout.flush()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Done"))
