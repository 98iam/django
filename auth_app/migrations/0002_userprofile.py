# Generated by Django 5.2 on 2025-04-12 04:53

import auth_app.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth_app", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
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
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                (
                    "profile_image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=auth_app.models.profile_image_path,
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        choices=[
                            ("en", "English"),
                            ("es", "Spanish"),
                            ("fr", "French"),
                            ("de", "German"),
                        ],
                        default="en",
                        max_length=10,
                    ),
                ),
                (
                    "timezone",
                    models.CharField(
                        choices=[
                            ("UTC", "UTC"),
                            ("US/Eastern", "US/Eastern"),
                            ("US/Central", "US/Central"),
                            ("US/Pacific", "US/Pacific"),
                            ("Europe/London", "Europe/London"),
                            ("Europe/Paris", "Europe/Paris"),
                            ("Asia/Tokyo", "Asia/Tokyo"),
                        ],
                        default="UTC",
                        max_length=50,
                    ),
                ),
                (
                    "date_format",
                    models.CharField(
                        choices=[
                            ("MM/DD/YYYY", "MM/DD/YYYY"),
                            ("DD/MM/YYYY", "DD/MM/YYYY"),
                            ("YYYY-MM-DD", "YYYY-MM-DD"),
                        ],
                        default="MM/DD/YYYY",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email_notifications", models.BooleanField(default=True)),
                ("low_stock_alerts", models.BooleanField(default=True)),
                ("order_updates", models.BooleanField(default=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
