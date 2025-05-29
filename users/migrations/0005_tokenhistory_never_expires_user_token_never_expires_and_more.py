from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_user_keep_token_history"),
    ]

    operations = [
        migrations.AddField(
            model_name="tokenhistory",
            name="never_expires",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="token_never_expires",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="tokenhistory",
            name="expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
