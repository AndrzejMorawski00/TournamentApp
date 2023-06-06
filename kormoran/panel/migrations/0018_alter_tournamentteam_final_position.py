# Generated by Django 4.2 on 2023-05-31 18:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0017_tournament_ladder_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournamentteam',
            name='final_position',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
