# Generated by Django 5.0.3 on 2024-03-28 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theatre", "0005_alter_performance_play"),
    ]

    operations = [
        migrations.AlterField(
            model_name="play",
            name="actors",
            field=models.ManyToManyField(
                null=True, related_name="plays", to="theatre.actor"
            ),
        ),
        migrations.AlterField(
            model_name="play",
            name="genres",
            field=models.ManyToManyField(
                null=True, related_name="plays", to="theatre.genre"
            ),
        ),
    ]
