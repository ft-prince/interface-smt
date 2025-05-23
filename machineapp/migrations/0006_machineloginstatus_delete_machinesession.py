# Generated by Django 5.1.5 on 2025-01-19 21:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("machineapp", "0005_alter_machinesession_machine"),
    ]

    operations = [
        migrations.CreateModel(
            name="MachineLoginStatus",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("device_id", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "machine",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="login_status",
                        to="machineapp.machine",
                    ),
                ),
            ],
            options={
                "unique_together": {("machine", "device_id")},
            },
        ),
        migrations.DeleteModel(
            name="MachineSession",
        ),
    ]
