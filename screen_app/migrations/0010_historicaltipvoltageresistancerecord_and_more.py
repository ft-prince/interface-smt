# Generated by Django 5.1.7 on 2025-05-15 15:03

import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("screen_app", "0009_historicalsolderpastecontrol_solderpastecontrol"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalTipVoltageResistanceRecord",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                ("department", models.CharField(default="Production", max_length=50)),
                ("operation", models.CharField(default="Rework", max_length=50)),
                ("month_year", models.DateField(default=django.utils.timezone.now)),
                (
                    "soldering_station_control_no",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("date", models.DateField(default=django.utils.timezone.now)),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("1st", "1st"),
                            ("2nd", "2nd"),
                            ("3rd", "3rd"),
                            ("4th", "4th"),
                        ],
                        max_length=5,
                    ),
                ),
                ("tip_voltage", models.FloatField(help_text="Should be less than 1V")),
                (
                    "tip_resistance",
                    models.FloatField(help_text="Should be less than 10Ω"),
                ),
                (
                    "operator_signature",
                    models.CharField(
                        choices=[("✔", "OK"), ("✘", "Not OK"), ("", "Not Checked")],
                        default="✔",
                        max_length=1,
                    ),
                ),
                (
                    "supervisor_signature",
                    models.CharField(
                        choices=[("✔", "OK"), ("✘", "Not OK"), ("", "Not Checked")],
                        default="✘",
                        max_length=1,
                    ),
                ),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("updated_at", models.DateTimeField(blank=True, editable=False)),
                (
                    "shift",
                    models.CharField(
                        blank=True,
                        choices=[("A", "A"), ("B", "B")],
                        max_length=1,
                        null=True,
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "operator",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "process_machine",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="screen_app.processmachinemapping",
                    ),
                ),
                (
                    "qsf_document",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="screen_app.qsf",
                    ),
                ),
            ],
            options={
                "verbose_name": "historical Tip Voltage & Resistance Record",
                "verbose_name_plural": "historical Tip Voltage & Resistance Records",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="TipVoltageResistanceRecord",
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
                ("department", models.CharField(default="Production", max_length=50)),
                ("operation", models.CharField(default="Rework", max_length=50)),
                ("month_year", models.DateField(default=django.utils.timezone.now)),
                (
                    "soldering_station_control_no",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("date", models.DateField(default=django.utils.timezone.now)),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("1st", "1st"),
                            ("2nd", "2nd"),
                            ("3rd", "3rd"),
                            ("4th", "4th"),
                        ],
                        max_length=5,
                    ),
                ),
                ("tip_voltage", models.FloatField(help_text="Should be less than 1V")),
                (
                    "tip_resistance",
                    models.FloatField(help_text="Should be less than 10Ω"),
                ),
                (
                    "operator_signature",
                    models.CharField(
                        choices=[("✔", "OK"), ("✘", "Not OK"), ("", "Not Checked")],
                        default="✔",
                        max_length=1,
                    ),
                ),
                (
                    "supervisor_signature",
                    models.CharField(
                        choices=[("✔", "OK"), ("✘", "Not OK"), ("", "Not Checked")],
                        default="✘",
                        max_length=1,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "shift",
                    models.CharField(
                        blank=True,
                        choices=[("A", "A"), ("B", "B")],
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    "operator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tip_voltage_records_as_operator",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "process_machine",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="TipVoltageResistanceRecords",
                        to="screen_app.processmachinemapping",
                    ),
                ),
                (
                    "qsf_document",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="TipVoltageResistanceRecords",
                        to="screen_app.qsf",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tip Voltage & Resistance Record",
                "verbose_name_plural": "Tip Voltage & Resistance Records",
                "ordering": ["-date", "frequency"],
            },
        ),
    ]
