# Generated by Django 4.2 on 2023-06-06 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0019_alter_tournamentteam_ladder_choice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='ladder_size',
        ),
    ]