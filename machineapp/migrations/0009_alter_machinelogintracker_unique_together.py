# Generated by Django 5.1.7 on 2025-03-29 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("machineapp", "0008_machine_show_fixture_cleaning_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="machinelogintracker",
            unique_together=set(),
        ),
    ]
