# Generated by Django 4.2 on 2023-05-31 17:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0016_alter_tournamentteam_final_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='ladder_size',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1024)]),
        ),
    ]
