from .models import Match, TournamentMatch, Team, TournamentTeam
from django.db.models import Q


def calcualte_match_data(match_result, team_1_result, team_2_result):
    # Change match status
    match_result.match.match_status = Match.MatchStatus.COMPLETED
    match_result.match.team_1_result = team_1_result
    match_result.match.team_2_result = team_2_result
    team_1 = match_result.match.team_1
    team_2 = match_result.match.team_2
    # Change tournament team data
    tournament_team_1 = TournamentTeam.objects.filter(
        Q(team=team_1) & Q(tournament=match_result.tournament))[0]
    tournament_team_2 = TournamentTeam.objects.filter(
        Q(team=team_2) & Q(tournament=match_result.tournament))[0]
    print(tournament_team_1)
    print(tournament_team_2)
    tournament_team_1.points_scored += int(team_1_result)
    tournament_team_1.points_lost += int(team_2_result)
    tournament_team_2.points_scored+= int(team_2_result)
    tournament_team_2.points_lost += int(team_1_result)
    if team_1_result > team_2_result:
        tournament_team_1.team_won += 1
        tournament_team_2.team_lost += 1
    elif team_1_result < team_2_result:
        tournament_team_1.team_lost += 1
        tournament_team_2.team_won += 1
    else:
        tournament_team_1.team_draw += 1
        tournament_team_2.team_draw += 1
    # Change global team data
    if team_1_result > team_2_result:
        team_1.team_won += 1
        team_2.team_lost += 1
    elif team_1_result < team_2_result:
        team_1.team_lost += 1
        team_2.team_won += 1
    else:
        team_1.team_draw += 1
        team_2.team_draw += 1
    # Save data
    match_result.match.save()
    team_1.save()
    team_2.save()
    tournament_team_1.save()
    tournament_team_2.save()
