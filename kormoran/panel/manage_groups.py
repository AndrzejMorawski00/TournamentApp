
from .models import Tournament, TournamentTeam, TournamentMatch, Match
from django.db.models import Q

from random import shuffle
from . import manage_tournament
import math
# Groups


def pairs(n):
    return [[a, b] for a in range(n) for b in range(a, n) if a != b]


def generate_group_number(tournament_type):
    if tournament_type == Tournament.TournamentType.GROUP2:
        return 2
    elif tournament_type == Tournament.TournamentType.GROUP3:
        return 3
    elif tournament_type == Tournament.TournamentType.GROUP4:
        return 4
    return 1


def print_groups(tournament: Tournament):

    group_number = generate_group_number(tournament.tournament_type)
    for i in range(1, group_number + 1):
        print("Group: ", i)
        teams = TournamentTeam.objects.filter(
            Q(tournament=tournament) & Q(group_choice=i))
        for team in list(teams):
            print("Team:", team)


def assign_teams_to_groups(tournament: Tournament):
    group_number = generate_group_number(tournament.tournament_type)
    teams = TournamentTeam.objects.filter(tournament=tournament)
    manage_tournament.set_selected_false(list(teams))
    group_sizes = []
    if len(list(teams)) % group_number == 0:
        for i in range(group_number):
            group_sizes.append(len(list(teams)) // group_number)
    else:
        for i in range(group_number - 1):
            group_sizes.append(len(list(teams)) // group_number)
        group_sizes.append(
            len(list(teams)) - (((len(list(teams)) // group_number) * (group_number - 1))))
    # Select teams to group
    for i in range(len(group_sizes)):
        group_teams = list(teams.filter(
            Q(group_choice=(i + 1)) & Q(selected=False)))[0:group_sizes[i]]
        manage_tournament.set_selected_true(group_teams)

    # Select rest of the teams/unselected ones
    for i in range(len(group_sizes)):
        selected_teams = teams.filter(Q(group_choice=i + 1) & Q(selected=True))
        unselected_teams = list(teams.filter(selected=False))
        shuffle(unselected_teams)
        if len(selected_teams) < group_sizes[i]:
            new_teams = unselected_teams[0:(
                group_sizes[i] - len(selected_teams))]
            for team in new_teams:
                team.group_choice = i + 1
                team.selected = True
                team.save()
    
    

    

def save_groups(groups):
    for i in range(len(groups)):  # Iterate for groups
        for j in range(len(groups[i])):  # Iterate in single group
            groups[i][j].group_choice = i + 1
            groups[i][j].save()


def reset_groups(teams):
    for team in teams:
        team.group_choice = 0
        team.save()


# Generate Matches in groups:


def generate_group_matches(tournament: Tournament):
    matches_left = 0
    groups = generate_group_number(tournament.tournament_type)
    for group in range(groups):
        teams = list(TournamentTeam.objects.filter(
            Q(tournament=tournament) & Q(group_choice=group + 1)))
        list_of_pairs = pairs(len(teams))
        matches_left += len(list_of_pairs)
        for pair in list_of_pairs:
            manage_tournament.generate_match(
                teams[pair[0]], teams[pair[1]], tournament)
    manage_tournament.update_match_left(tournament, matches_left)

    reset_teams = list(TournamentTeam.objects.filter(Q(tournament = tournament) & Q(selected = True)))
    manage_tournament.set_selected_false(reset_teams)


# Assing team to a group:

def assign_groups(tournament, team_dict):
    for team in team_dict:
        selected_team = TournamentTeam.objects.get(
            Q(tournament=tournament) & Q(team=team))
        if team_dict[team] != "r":
            selected_team.group_choice = team_dict[team]
        else:
            selected_team.group_choice = 0
        selected_team.save()
