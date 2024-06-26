# Generated by Django 5.0.3 on 2024-03-28 16:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("theatre", "0009_alter_play_actors_alter_play_genres"),
    ]

    operations = [
        migrations.AlterField(
            model_name="performance",
            name="play",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="theatre.play"
            ),
        ),
    ]
