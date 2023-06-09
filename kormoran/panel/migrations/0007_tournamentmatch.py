# Generated by Django 4.2 on 2023-05-09 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0006_remove_team_selected_tournamentteam_selected'),
    ]

    operations = [
        migrations.CreateModel(
            name='TournamentMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel.match')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel.tournament')),
            ],
        ),
    ]
