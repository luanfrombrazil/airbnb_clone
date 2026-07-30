import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Property",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=120)),
                ("price_per_night", models.DecimalField(decimal_places=2, max_digits=10)),
                ("max_guests", models.PositiveIntegerField(default=1)),
                ("amenities", models.JSONField(blank=True, default=list)),
                ("rating", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "host",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="properties",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name_plural": "properties", "ordering": ["-rating", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("check_in", models.DateField()),
                ("check_out", models.DateField()),
                ("guests_count", models.PositiveIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pendente"), ("APPROVED", "Aprovada"), ("REJECTED", "Recusada")],
                        default="PENDING",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "guest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reservations",
                        to="listings.property",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="PropertyImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.URLField(max_length=500)),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="listings.property",
                    ),
                ),
            ],
        ),
    ]
