# Generated by Django 4.2 on 2023-05-09 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0005_team_selected'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='selected',
        ),
        migrations.AddField(
            model_name='tournamentteam',
            name='selected',
            field=models.BooleanField(default=False),
        ),
    ]