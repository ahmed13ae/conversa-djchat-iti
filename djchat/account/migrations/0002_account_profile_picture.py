# Generated by Django 4.2 on 2023-11-22 18:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="profile_picture",
            field=models.ImageField(blank=True, null=True, upload_to="account/"),
        ),
    ]
