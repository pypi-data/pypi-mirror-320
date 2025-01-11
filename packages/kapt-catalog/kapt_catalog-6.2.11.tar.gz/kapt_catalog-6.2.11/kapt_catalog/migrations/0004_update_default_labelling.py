from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("kapt_catalog", "0003_auto_20200527_0856"),
    ]

    operations = []

    # We are not able to execute update_default_labelling method
    # on a migration.
    # So the migration is doing nothing.
    # You have to execute manually the script in the
    # Migrating to kapt-catalog>=4.1.0 section of the README.rst
