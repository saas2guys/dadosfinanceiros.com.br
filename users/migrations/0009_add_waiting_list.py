# Generated by Django 5.2.1 on 2025-06-01 02:49

import uuid

import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_user_current_period_end_user_current_period_start"),
    ]

    operations = [
        migrations.CreateModel(
            name="WaitingList",
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
                ("email", models.EmailField(max_length=254, unique=True)),
                ("first_name", models.CharField(blank=True, max_length=30)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("company", models.CharField(blank=True, max_length=100)),
                ("use_case", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_notified", models.BooleanField(default=False)),
                ("notified_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "Waiting List Entry",
                "verbose_name_plural": "Waiting List Entries",
                "ordering": ["created_at"],
            },
        ),
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name="plan",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="user",
            name="subscription_started_at",
        ),
        migrations.AddField(
            model_name="plan",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="is_free",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="plan",
            name="price_yearly",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="stripe_yearly_price_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name="plan",
            name="daily_request_limit",
            field=models.PositiveIntegerField(default=1000),
        ),
        migrations.AlterField(
            model_name="plan",
            name="features",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="plan",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="plan",
            name="price_monthly",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
            ),
        ),
        migrations.AlterField(
            model_name="plan",
            name="stripe_price_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="current_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="users.plan",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="daily_requests_made",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="previous_tokens",
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name="user",
            name="request_token",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="subscription_status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("inactive", "Inactive"),
                    ("canceled", "Canceled"),
                    ("past_due", "Past Due"),
                    ("incomplete", "Incomplete"),
                    ("incomplete_expired", "Incomplete Expired"),
                    ("trialing", "Trialing"),
                    ("unpaid", "Unpaid"),
                ],
                default="inactive",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="token_validity_days",
            field=models.PositiveIntegerField(default=30),
        ),
    ]
