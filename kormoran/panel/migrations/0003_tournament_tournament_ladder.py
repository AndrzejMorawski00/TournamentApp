# Generated by Django 4.2 on 2023-05-09 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0002_remove_tournament_matches_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='tournament_ladder',
            field=models.BooleanField(default=False),
        ),
    ]