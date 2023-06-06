from .models import Tournament, TournamentTeam, TournamentMatch, Match
from django.db.models import Q

from random import shuffle
import math
from . import manage_tournament


def generate_ladder_size(tournament: Tournament) -> int:

    team_list = list(TournamentTeam.objects.filter(
        Q(tournament=tournament) & Q(selected=True)))
    manage_tournament.update_match_left(tournament, len(team_list))
    ladder_size = int(math.pow(2, math.floor(math.log2(len(team_list)))))
    tournament.save()
    return ladder_size


def assign_ladder_teams(teams, tournament: Tournament):
    set_default_position(tournament)
    taken_positions = []
    for key in teams:  # key -> id teams[key] -> position
        if update_position(key, teams[key], tournament, taken_positions):
            taken_positions.append(teams[key])

    teams_left = list(TournamentTeam.objects.filter(
        Q(tournament=tournament) & Q(selected=True) & Q(ladder_choice=0)))

    counter = 1
    while len(teams_left):
        shuffle(teams_left)
        team = teams_left[0]

        if counter not in taken_positions:
            update_position(team.team, counter, tournament, taken_positions)
            taken_positions.append(counter)
        counter += 1
        teams_left = list(TournamentTeam.objects.filter(
            Q(tournament=tournament) & Q(selected=True) & Q(ladder_choice=0)))


def update_position(team: TournamentTeam, position, tournament, taken_positions) -> int:
    team = list(TournamentTeam.objects.filter(
        Q(tournament=tournament) & Q(team=team)))[0]
    if team.ladder_choice == 0 and position not in taken_positions:
        team.ladder_choice = position
        team.save()
        return position
    return 0


def generate_ladder_matches(tournament: Tournament):
    team_list = list(TournamentTeam.objects.filter(
        Q(tournament=tournament) & Q(selected=True)).order_by("ladder_choice"))

    ladder_size = 2 ** int(math.floor(math.log2(len(team_list))))

    if len(team_list) == 4:
        generate_ladder_final(tournament)
    elif len(team_list) == 2:
        generate_last_2_matches(tournament)
    else:
        if ladder_size < len(team_list) and len(team_list) > 2:
            generate_eliminations_matches(ladder_size, team_list, tournament)
        else:
            generate_matches(team_list, tournament)
        tournament.save()


def generate_ladder_final(tournament: Tournament):
  
    team_list = list(TournamentTeam.objects.filter(
        Q(tournament=tournament) & Q(selected=True)).order_by("ladder_choice"))
    for team in team_list:
        team.final_position += 10
        team.save()
    generate_matches(team_list, tournament)


def generate_last_2_matches(tournament: Tournament):
    team_list = TournamentTeam.objects.filter(
        Q(tournament=tournament)).order_by("-final_position")
    final_teams = list(team_list.filter(selected=True))
    for team in final_teams:
        team.final_position += 10
        team.save()
    third_place_teams = list(team_list.exclude(selected=True))[:2]
    generate_matches(final_teams, tournament)
    generate_matches(third_place_teams, tournament)


def generate_matches(team_list, tournament: Tournament):
    for i in range(0, len(team_list), 2):
        team_1 = team_list[i]
        team_2 = team_list[i + 1]
        manage_tournament.generate_match(team_1, team_2, tournament)



def generate_eliminations_matches(ladder_size, teams, tournament: Tournament):
    matches_left = len(teams) - ladder_size
    selected_teams = teams[0: 2 * matches_left]
    generate_matches(selected_teams, tournament)
   


def set_default_position(tournament: Tournament):
    teams = list(TournamentTeam.objects.filter(
        Q(tournament=tournament) & Q(selected=True)))
    for team in teams:
        team.ladder_choice = 0
        team.save()


