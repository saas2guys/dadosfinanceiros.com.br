from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="previous_tokens",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="user",
            name="token_auto_renew",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="token_validity_days",
            field=models.IntegerField(default=30),
        ),
    ]
