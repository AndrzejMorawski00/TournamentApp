from django import forms
from django.forms import ModelForm
from .models import TempTeam, Sport, Tournament, Match


class SportForm(ModelForm):
    class Meta:
        model = Sport
        fields = ["sport_name", "sport_gender"]

class TempTeamForm(ModelForm):
    class Meta:
        model = TempTeam
        exclude = ["temp_user", "temp_id"]

class TournamentForm(ModelForm):
    class Meta:
        model = Tournament
        fields = ["tournament_sport", "tournament_name", "tournament_type"]
    
    
class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ['team_1_result', 'team_2_result']
