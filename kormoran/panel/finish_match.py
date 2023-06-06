from .models import Match, Tournament, TournamentMatch, Team, TournamentTeam
from django.db.models import Q

from . import manage_tournament
from . import manage_ladder


def calcualte_match_data(match_result: TournamentMatch, team_1_result: int, team_2_result: int):
    # Change match status
    match_result.match.match_status = Match.MatchStatus.COMPLETED
    match_result.match.team_1_result = team_1_result
    match_result.match.team_2_result = team_2_result
    if match_result.tournament.tournament_status == Tournament.TournamentStatus.GROUP:
        finish_group_match(match_result, team_1_result, team_2_result)
    elif match_result.tournament.tournament_status == Tournament.TournamentStatus.LADDER:
        finish_ladder_match(match_result, team_1_result, team_2_result)
    match_result.save()
    change_matches_left(match_result.tournament)
    match_result.match.save()


def finish_group_match(match_result: TournamentMatch, team_1_result: int, team_2_result: int):
    team_1 = match_result.match.team_1
    team_2 = match_result.match.team_2
    tournament = match_result.tournament
    tournament_team_1 = TournamentTeam.objects.get(
        Q(team=team_1) & Q(tournament=tournament))
    tournament_team_2 = TournamentTeam.objects.get(
        Q(team=team_2) & Q(tournament=tournament))
    # Change points gained and lost:
    tournament_team_1.points_scored += team_1_result
    tournament_team_2.points_scored += team_2_result

    tournament_team_1.points_lost += team_2_result
    tournament_team_2.points_lost += team_1_result

    # Change tournament won lost draws
    if team_1_result > team_2_result:
        tournament_team_1.team_won += 1
        tournament_team_2.team_lost += 1
    elif team_1_result == team_2_result:
        tournament_team_1.team_draw += 1
        tournament_team_2.team_draw += 1
    else:
        tournament_team_1.team_lost += 1
        tournament_team_2.team_won += 1

    # Change global won lost draws

    # Save Data
    match_result.save()
    tournament_team_1.save()
    tournament_team_2.save()
    tournament.save()
    team_1.save()
    team_2.save()

    update_global_team_stats(
        tournament_team_1.team, tournament_team_2.team, team_1_result, team_2_result)
    calculate_team_points(tournament_team_1)
    calculate_team_points(tournament_team_2)
    calcualte_team_balance(tournament_team_1)
    calcualte_team_balance(tournament_team_2)


def finish_ladder_match(match_result: TournamentMatch, team_1_result: int, team_2_result: int):
    team_1 = match_result.match.team_1
    team_2 = match_result.match.team_2
    tournament = match_result.tournament
    tournament_team_1 = TournamentTeam.objects.get(
        Q(team=team_1) & Q(tournament=tournament))
    tournament_team_2 = TournamentTeam.objects.get(
        Q(team=team_2) & Q(tournament=tournament))

    # Change tournament team stats
    if team_1_result > team_2_result:
        tournament_team_1.final_position += 1
        tournament_team_2.selected = False
    elif team_1_result == team_2_result:
        match_result.match.match_status = Match.MatchStatus.PENDING
        match_result.match.user = None
        match_result.match.team_1_result = 0
        match_result.match.team_2_result = 0
    else:
        tournament_team_1.selected = False
        tournament_team_2.final_position += 1
    # Change global team stats

    update_global_team_stats(
        tournament_team_1.team, tournament_team_2.team, team_1_result, team_2_result)

    if tournament.matches_left > 0:
        tournament_match_list = TournamentMatch.objects.filter(
            Q(tournament=tournament))
        finished_match_list = []
        for match in tournament_match_list:
            if match.match.match_status == Match.MatchStatus.COMPLETED:
                finished_match_list.append(match)
        if len(list(tournament_match_list)) == len(finished_match_list):
            manage_ladder.generate_ladder_matches(tournament)

    match_result.save()
    match_result.match.save()
    tournament_team_1.save()
    tournament_team_2.save()
    team_1.save()
    team_2.save()


def update_global_team_stats(team_1, team_2, team_1_result, team_2_result):
    if team_1_result > team_2_result:
        team_1.team_won += 1
        team_2.team_lost += 1
    elif team_1_result < team_2_result:
        team_1.team_lost += 1
        team_2.team_won += 1
    else:
        team_1.team_draw += 1
        team_2.team_draw += 1
    team_1.save()
    team_2.save()


def calculate_team_points(team: TournamentTeam):
    sport = team.team.team_sport
    points = team.team_won * sport.points_win + team.team_lost * \
        sport.points_lost + team.team_draw * sport.points_draw
    team.team_points = points
    team.save()


def calcualte_team_balance(team: TournamentTeam):
    team.points_balance = team.points_scored - team.points_lost
    team.save()


def change_matches_left(tournament: Tournament):
    tournament = Tournament.objects.get(tournament_id=tournament.tournament_id)
    if tournament.matches_left == 1:
        manage_tournament.change_tournament_status(tournament)

    tournament.matches_left -= 1

    tournament.save()

    all_matches = list(TournamentMatch.objects.all())
    matches_finished = []

    for match in all_matches:
        match.save()
        if match.match.match_status == Match.MatchStatus.COMPLETED:
            matches_finished.append(match)

    if len(matches_finished) == len(all_matches) and tournament.matches_left > 0:

        manage_ladder.generate_ladder_matches(tournament)
