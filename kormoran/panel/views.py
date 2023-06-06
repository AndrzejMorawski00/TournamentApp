from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from django.http import HttpRequest

from .decorators import user_authenticated, user_not_authenticated, group_based_access
from .models import TempTeam, Sport, Team, Tournament, TournamentTeam, TournamentMatch, Match
from .forms import SportForm, TempTeamForm, TournamentForm, MatchForm

from . import manage_tournament, manage_groups, manage_ladder
from . import finish_match

# Main view


def index(request):
    referee = True if request.user.groups.filter(name__in=['referee']).exists() else False
    it = True if request.user.groups.filter(name__in=['it']).exists() else False
    return render(request, "panel/home.html", {"referee" : referee , "it" : it})


# View to add new temp teams
@user_authenticated
def add_team(request):
    if request.method == "POST":
        team_form = TempTeamForm(request.POST)
        team_form.instance.temp_user = request.user
        if team_form.is_valid():
            team_form.save()
            messages.success(request, "Team added successfully")
            return redirect("panel:add-team-view")
        else:
            for error in list(team_form.errors.values()):
                messages.error(request, error)
    else:
        team_form = TempTeamForm()

    return render(request, "panel/new-team.html", {"team_form": team_form})

# View confirm temp added teams


@group_based_access(groups=['it'])
def confirm_team(request):
    team_list = list(TempTeam.objects.all())
    return render(request, "panel/confirm-team.html", {"team_list": team_list})

# View that confirms/deletes teams


@group_based_access(groups=['it'])
def confirm_single(request, team_id, operation):
    temp_team = list(TempTeam.objects.filter(temp_id=team_id))[0]
    if operation == 'add':
        if len(list(Team.objects.filter(team_name=temp_team.temp_name, team_sport=temp_team.temp_sport))):
            messages.error(request, "Team Already Exists")
        else:
            team = Team(team_name=temp_team.temp_name,
                        team_sport=temp_team.temp_sport)
            team.save()
            messages.success(request, "Team added successfully")
    elif operation == 'remove':
        messages.success(request, "Team removed successfully")

    else:
        messages.error(request, "Invalid Operation")
        return redirect("panel:confirm-team-view")

    temp_team.delete()
    return redirect("panel:confirm-team-view")

# View to add new sport


@group_based_access(groups=['it'])
def add_sport(request):
    if request.method == "POST":
        sport_form = SportForm(request.POST)

        if sport_form.is_valid():
            slug_text = slugify(
                f"{ sport_form['sport_name'].value()} {sport_form['sport_gender'].value()}")
            if len(list(Sport.objects.filter(sport_slug=slug_text))):
                messages.error(request, "Sport allready Exists")
            else:
                sport_form.save()
                messages.success(request, "Sport added successfully")

            return redirect("panel:add-sport-view")

        else:
            for error in list(sport_form.errors.values()):
                messages.error(request, error)
    else:
        sport_form = SportForm()

    return render(request, "panel/new-sport.html", {"sport_form": sport_form, })


# View to create new tournament:

@group_based_access(groups=['it'])
def create_tournament(request):
    if request.method == "POST":
        tournament_form = TournamentForm(request.POST)
        if tournament_form.is_valid():
            tournament_name = tournament_form['tournament_name'].value()
            if list(Tournament.objects.filter(tournament_name=tournament_name)):
                messages.error(request, "This name is already Taken")
            else:
                tournament_form.save()
                messages.success(request, "Tournament Created successfully")
                tournament_id = list(Tournament.objects.filter(
                    tournament_name=tournament_name))[0].tournament_id
                return redirect("panel:add-tournament-teams-view", tournament_id=tournament_id)

        else:
            for error in list(tournament_form.errors.values()):
                messages.error(request, error)

    else:
        tournament_form = TournamentForm()
    return render(request, "panel/new-tournament.html", {"tournament_form": tournament_form})


# View to add teams to a new tournament
@group_based_access(groups=['it'])
def add_tournament_teams(request, tournament_id):
    result_teams = []
    tournament = Tournament.objects.get(tournament_id=tournament_id)
    tournament_teams = TournamentTeam.objects.filter(tournament=tournament)
    teams = Team.objects.filter(team_sport=tournament.tournament_sport)
    for team in teams:
        if len(list(tournament_teams.filter(team=team))) == 0:
            result_teams.append(team)

    if len(result_teams) == 0:
        return redirect("panel:manage-tournament-view")

    if request.method == "POST":
        for team in result_teams:
            if request.POST.get(f"checked_{team.team_id}"):
                new_team = TournamentTeam(team=team, tournament=tournament)
                new_team.selected = True
                new_team.save()
        return redirect("panel:add-tournament-teams-view", tournament_id=tournament_id)

    return render(request, "panel/add-tournament-teams.html", {"team_list": result_teams})


# View to manage created tournament

@group_based_access(groups=['it'])
def manage_tournaments(request):
    if request.method == "POST":
        tournament_id = request.POST['data']
        remove = True if request.POST.get('delete') else False
        confirm = True if request.POST.get('confirm') else False
     
        tournament = Tournament.objects.get(tournament_id=tournament_id)

        if confirm:
            manage_tournament.change_tournament_status(tournament)

        if remove:
            tournament.delete()
            messages.error(request, "Tournament Removed Successfully")

    tournament_list = list(Tournament.objects.all())
    result_dict = {}
    link_dict = {}
    for tournament in tournament_list:
        teams = list(TournamentTeam.objects.filter(tournament=tournament))
        link_data = manage_tournament.return_tournament_link(tournament)

        result_dict[(tournament, link_data)] = teams
    return render(request, "panel/manage-tournaments.html", {"result_dict": result_dict, "link_dict": link_dict})


# remove Team from tournament

@group_based_access(groups=['it'])
def remove_team(request, tournament_id, team_id):
    team = TournamentTeam.objects.filter(
        Q(team=team_id) & Q(tournament=tournament_id))
    team.delete()
    messages.success(request, "Team was removed successfully")
    return redirect("panel:manage-tournament-view")

# View every tournament - every user


def view_tournaments(request):
    tournament_list = Tournament.objects.all()

    return render(request, "panel/all-tournaments.html", {"tournament_list": tournament_list})


# View tournament matches - every user + RABC for manage matches

def view_matches(request: HttpRequest, tournament_id):
    if request.method == "POST":
        if request.POST.get('match-id'):
            return redirect("panel:manage-match-view", match_id=request.POST.get('match-id'))

    match_list = TournamentMatch.objects.filter(tournament_id=tournament_id)
    return render(request, "panel/tournament-matches.html", {"match_list": match_list, "access": request.user.groups.filter(name__in=['referee']).exists()})

# View to manage a match


@group_based_access(groups=['referee'])
def manage_match(request, match_id):
    match = Match.objects.get(pk=match_id)
    match_data = list(TournamentMatch.objects.filter(match=match))[0]

    if match_data.match.match_status == Match.MatchStatus.PENDING:
        match_data.match.match_status = Match.MatchStatus.DURING
        match_data.match.user = request.user
        match_data.match.save()

    if request.method == "POST":
        if request.POST.get('finish'):
            team_1_result = request.POST['team_1_result']
            team_2_result = request.POST['team_2_result']
            finish_match.calcualte_match_data(
                match_data, int(team_1_result), int(team_2_result))
            return redirect("panel:tournament-list-view")

        elif request.POST.get('cancel'):
            match_data.match.team_1_result = 0
            match_data.match.team_2_result = 0
            match_data.match.match_status = Match.MatchStatus.PENDING
            match_data.match.user = None
            match_data.match.save()
            return redirect("panel:tournament-list-view")
        elif request.POST.get('save'):

            match_form = MatchForm(request.POST or None)
            if match_form.is_valid():
                match_data.match.team_1_result = request.POST['team_1_result']
                match_data.match.team_2_result = request.POST['team_2_result']
                match_data.match.save()

            else:
                for error in match_form.errors:
                    messages.error(request, error)

        else:
            messages.error(request, "Error occured during saving match data")

    match_form = MatchForm(instance=match_data.match)

    return render(request, "panel/manage-match.html", {"match_form": match_form})


# View to see matches assigned to a referee profile
@group_based_access(groups=['referee'])
def my_matches(request):
    match_list = Match.objects.filter(user=request.user)

    return render(request, "panel/my-matches.html", {"match_list": match_list})


@group_based_access(groups=['it'])
def tournament_actions(request: HttpRequest, redirect_link, tournament_id):
    return redirect(f"panel:{redirect_link}", tournament_id=tournament_id)

# Set Tournament Groups
# Zrobić to tak, żeby można było pod to samo podpiać darbinkę + wyświetalnanie defaultowych


@group_based_access(groups=['it'])
def set_groups(request, tournament_id):
    tournament = Tournament.objects.get(tournament_id=tournament_id)
    team_list = TournamentTeam.objects.filter(Q(tournament = tournament))
    
    if request.method == "POST":
        teams_to_assign = {}
        for object in request.POST:
            if "select_" in str(object):
                team_id = str(object).split("_")[1]
                value = request.POST.get(object)
                if value != "r":
                    value = int(value)
                teams_to_assign[team_id] = value

        manage_groups.assign_groups(tournament_id, teams_to_assign)
        manage_groups.assign_teams_to_groups(
            Tournament.objects.get(tournament_id=tournament_id))
        return redirect("panel:manage-tournament-view")
    team_list = TournamentTeam.objects.filter(tournament=tournament)

    return render(request, "panel/set-groups.html", {"team_list": team_list, "group_counter": range(1, manage_groups.generate_group_number(tournament.tournament_type) + 1)})


@group_based_access(groups=['it'])
def set_ladder(request: HttpRequest, tournament_id):
    tournament = Tournament.objects.get(tournament_id=tournament_id)
    team_positions = manage_ladder.generate_ladder_size(tournament)
    if len(list(TournamentTeam.objects.filter(Q(tournament=tournament) & Q(selected=True)))) > team_positions:
        team_positions *= 2
    if request.method == "POST":
        teams_to_assign = {}
        for object in request.POST:
            if "select_" in str(object):
                team_id = str(object).split("_")[1]
                value = int(request.POST.get(object))
                if value != 0:
                    teams_to_assign[team_id] = value

        manage_ladder.assign_ladder_teams(teams_to_assign, tournament)

    if tournament.tournament_type == Tournament.TournamentType.LADDER:
        team_list = TournamentTeam.objects.filter(tournament=tournament)
    else:

        team_list = TournamentTeam.objects.filter(
            Q(tournament=tournament) & Q(selected=True))

    return render(request, "panel/set-ladder.html", {"team_list": team_list, "team_positions":  team_positions})


@group_based_access(groups=['it'])
def choose_teams(request: HttpRequest, tournament_id):
    tournament = Tournament.objects.get(tournament_id=tournament_id)
    if request.method == "POST":
        team_list = TournamentTeam.objects.filter(Q(tournament=tournament_id))
        for object in request.POST:
            if "checked_" in object:
                team_id = str(object).split("_")[1]
                team = TournamentTeam.objects.get(
                    Q(team=team_id) & Q(tournament=tournament_id))
                team.selected = True
                team.save()

    team_list = TournamentTeam.objects.filter(Q(tournament=tournament))
    groups = list(team_list.order_by('-group_choice'))[0].group_choice

    group_dict = {}
    for group in range(1, groups + 1):
        group_dict[group] = list(team_list.filter(
            Q(group_choice=group)).order_by("-team_points", "-points_balance"))
    return render(request, "panel/choose-teams.html", {"group_dict": group_dict})
