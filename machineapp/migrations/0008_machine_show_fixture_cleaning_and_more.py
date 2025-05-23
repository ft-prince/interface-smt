# Generated by Django 5.1.7 on 2025-03-29 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("machineapp", "0007_machinelogintracker"),
    ]

    operations = [
        migrations.AddField(
            model_name="machine",
            name="show_fixture_cleaning",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="machine",
            name="show_maintenance_checklist",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="machine",
            name="show_pchart",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="machine",
            name="show_reading_list",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="machine",
            name="show_rejection_sheets",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="machine",
            name="show_soldering_bit",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="machine",
            name="show_startup_checklist",
            field=models.BooleanField(default=True),
        ),
    ]
