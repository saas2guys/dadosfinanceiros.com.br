from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0003_tokenhistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="keep_token_history",
            field=models.BooleanField(default=True),
        ),
    ]
