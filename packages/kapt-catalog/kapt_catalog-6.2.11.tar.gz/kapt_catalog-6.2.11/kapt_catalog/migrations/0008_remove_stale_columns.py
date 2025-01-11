from django.db import connection, migrations


def forwards_func(apps, schema_editor):
    print("\n  Looking for columns to remove...")

    # Describe each table name as a key and each field of
    # this table into a list
    operations = {
        "kapt_catalog_structure": ["status_id"],
        "kapt_catalog_description": [
            "automated_translations_fr",
            "automated_translations_en",
            "automated_translations_es",
            "automated_translations_it",
            "automated_translations_de",
            "automated_translations_nl",
        ],
    }

    for table_name, columns_to_remove in operations.items():
        with connection.cursor() as cursor:
            sql = (
                "select column_name "
                "from INFORMATION_SCHEMA.COLUMNS "
                f"where table_name = '{table_name}';"
            )
            cursor.execute(sql)

            existing_db_columns = [field[0] for field in list(cursor)]

            for column_to_remove in columns_to_remove:
                if column_to_remove in existing_db_columns:
                    cursor.execute(
                        f"alter table {table_name} drop column {column_to_remove};"
                    )
                    print(f'  Delete field "{column_to_remove}" in "{table_name}"')
                else:
                    print(f'  No field "{column_to_remove}" found in "{table_name}"')


def reverse_func(apps, schema_editor):
    # Nothing to reverse
    pass


class Migration(migrations.Migration):
    dependencies = [("kapt_catalog", "0007_auto_20201014_1337")]

    operations = [migrations.RunPython(forwards_func, reverse_func)]
