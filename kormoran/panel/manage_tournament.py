from .models import Tournament, TournamentTeam, TournamentMatch, Match
from django.db.models import Q

from random import shuffle
import math
from . import manage_groups
from . import manage_ladder
# General functions


def generate_match(team_1, team_2, tournament):
    new_match = Match(team_1=team_1.team, team_2=team_2.team,
                      sport=tournament.tournament_sport)
    new_match.save()
    tournament_match = TournamentMatch(
        match=new_match, tournament=tournament)
    tournament_match.save()

# Do przepisania


def manage_tournament(tournament_id):
    tournament = Tournament.objects.get(tournament_id=tournament_id)
    if tournament.tournament_status == Tournament.TournamentStatus.GROUP_PENDING:
        teams = TournamentTeam.objects.filter(Q(tournament = tournament) & Q(selected = True))
        if len(list(teams)):
            manage_groups.generate_group_matches(tournament)
    elif tournament.tournament_status == Tournament.TournamentStatus.LADDER_PENDING:
        teams = TournamentTeam.objects.filter(Q(tournament = tournament) & Q(selected = True))
        if len(list(teams)):
            manage_ladder.generate_ladder_matches(tournament)

    change_tournament_status(tournament)

    # teams = TournamentTeam.objects.filter(
    #     tournament=tournament).order_by('-group_choice')
    # # set_false(teams)
    # # reset_groups(teams)
    # manage_tournament.generate_ladder_matches(tournament)
    # # if tournament.tournament_type == "Ladder":
    # #     generate_ladder_matches()
    # # else:
    # #     groups = assign_teams_to_groups(teams, tournament)
    # #     generate_group_matches(groups, tournament)



def change_tournament_group_status(tournament: Tournament):
    if tournament.tournament_status == Tournament.TournamentStatus.GROUP_PENDING:
        manage_groups.generate_group_matches(tournament)
        tournament.tournament_status = Tournament.TournamentStatus.GROUP

    elif tournament.tournament_status == Tournament.TournamentStatus.GROUP:

        if "ldr" in tournament.tournament_type:

            tournament.tournament_status = Tournament.TournamentStatus.GROUP_FINISHED
            set_selected_false(
                list(TournamentTeam.objects.filter(tournament_id=tournament.tournament_id)))
        else:

            tournament.tournament_status = Tournament.TournamentStatus.COMPLETED
    elif tournament.tournament_status == Tournament.TournamentStatus.GROUP_FINISHED:

        tournament.tournament_status = Tournament.TournamentStatus.LADDER_PENDING
        manage_ladder.generate_ladder_size(tournament)


def change_tournament_ladder_status(tournament: Tournament):
    if tournament.tournament_status == Tournament.TournamentStatus.LADDER_PENDING:
        tournament.tournament_status = Tournament.TournamentStatus.LADDER
        manage_ladder.generate_ladder_matches(tournament)

    elif tournament.tournament_status == Tournament.TournamentStatus.LADDER:

        tournament.tournament_status = Tournament.TournamentStatus.COMPLETED


def change_tournament_status(tournament: Tournament):
    if tournament.tournament_type == Tournament.TournamentType.GROUP1:

        if tournament.tournament_status == Tournament.TournamentStatus.PENDING:

            tournament.tournament_status = Tournament.TournamentStatus.GROUP_PENDING
        else:

            change_tournament_group_status(tournament)
    elif "gr+ldr" in tournament.tournament_type:
        if tournament.tournament_status == Tournament.TournamentStatus.PENDING:
            tournament.tournament_status = Tournament.TournamentStatus.GROUP_PENDING
        else:
            change_tournament_ladder_status(tournament)
            change_tournament_group_status(tournament)

    elif "ldr" in tournament.tournament_type:
        if tournament.tournament_status == Tournament.TournamentStatus.PENDING:
            tournament.tournament_status = Tournament.TournamentStatus.LADDER_PENDING
        else:
            change_tournament_ladder_status(tournament)

    tournament.save()


def return_tournament_link(tournament: Tournament) -> tuple[str, str]:
    if tournament.tournament_status == Tournament.TournamentStatus.PENDING:
        return ("add-tournament-teams-view", "Add Teams")
    elif tournament.tournament_status == Tournament.TournamentStatus.GROUP_PENDING:
        return ("set-groups-view", "Set Groups")
    elif tournament.tournament_status == Tournament.TournamentStatus.LADDER_PENDING:
        return ("set-ladder-view", "Set Ladder")
    elif tournament.tournament_status == Tournament.TournamentStatus.GROUP_FINISHED:
        return ("choose-ladder-teams-view", "Choose Teams To Ladder")
    elif tournament.tournament_status == Tournament.TournamentStatus.COMPLETED:
        return ("", "Results")  # ToDo This link
    else:
        return ("", "Tournament in Progress")


def update_match_left(tournament: Tournament, matches: int):
    tournament.matches_left = matches
    tournament.save()


def set_selected_true(teams):
    for team in teams:
        team.selected = True
        team.save()


def set_selected_false(teams):
    for team in teams:
        team.selected = False
        team.save()
