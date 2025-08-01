# Generated by Django 5.2.1 on 2025-07-26 00:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0015_remove_apiusage_users_apius_user_id_14e7ee_idx_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="plan",
            options={},
        ),
        migrations.RemoveIndex(
            model_name="plan",
            name="users_plan_is_acti_3ae34b_idx",
        ),
        migrations.RemoveIndex(
            model_name="ratelimitcounter",
            name="users_ratel_identif_a03380_idx",
        ),
        migrations.RemoveIndex(
            model_name="ratelimitcounter",
            name="users_ratel_window__320c75_idx",
        ),
        migrations.RemoveIndex(
            model_name="ratelimitcounter",
            name="users_ratel_updated_5975cf_idx",
        ),
        migrations.RemoveIndex(
            model_name="usagesummary",
            name="users_usage_user_id_fb41b1_idx",
        ),
        migrations.RemoveIndex(
            model_name="usagesummary",
            name="users_usage_date_56c990_idx",
        ),
        migrations.RemoveIndex(
            model_name="usagesummary",
            name="users_usage_ip_addr_276fd3_idx",
        ),
        migrations.AlterUniqueTogether(
            name="ratelimitcounter",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="usagesummary",
            unique_together=set(),
        ),
    ]
