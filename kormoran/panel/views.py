from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from .decorators import user_authenticated, user_not_authenticated, group_based_access
from .models import TempTeam, Sport, Team, Tournament, TournamentTeam, TournamentMatch, Match
from .forms import SportForm, TempTeamForm, TournamentForm, MatchForm

from . import manage_tournament
from . import finish_match

# Main view
def index(request):
    return render(request, "panel/home.html", {})


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
    if request.method == "POST":

        # True ->  dodać False -> usunać
        op = False if request.POST.get('remove') else True
        print(request.POST)
        if op is True:
            pass
        else:
            pass
        return redirect("panel:confirm-team-view")

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
        return redirect("panel:confirm-tournament-view")

    if request.method == "POST":
        for team in result_teams:
            if request.POST.get(f"checked_{team.team_id}"):
                new_team = TournamentTeam(team=team, tournament=tournament)
                new_team.save()
        return redirect("panel:add-tournament-teams-view", tournament_id=tournament_id)

    return render(request, "panel/add-tournament-teams.html", {"team_list": result_teams})


# View to confirm created tournament

@group_based_access(groups=['it'])
def confirm_tournaments(request):
    if request.method == "POST":
        tournament_id = request.POST['data']
        remove = True if request.POST.get('delete') else False
        confirm = True if request.POST.get('confirm') else False

        tournament = Tournament.objects.get(tournament_id=tournament_id)

        if confirm:
            if "Group" in tournament.tournament_type:
                tournament.tournament_status = Tournament.TournamentStatus.GROUP
            else:
                tournament.tournament_status = Tournament.TournamentStatus.LADDER
            tournament.save()

            messages.success(request, "Tournament Added Successfully")

        if remove:
            tournament.delete()
            messages.error(request, "Tournament Removed Successfully")

    tournament_list = Tournament.objects.filter(tournament_status="pending")
    result_dict = {}
    link_dict = {}
    for tournament in tournament_list:
        teams = list(TournamentTeam.objects.filter(tournament=tournament))
        result_dict[tournament] = teams
    return render(request, "panel/confirm-tournaments.html", {"result_dict": result_dict, "link_dict": link_dict})


# remove Team from tournament

@group_based_access(groups=['it'])
def remove_team(request, tournament_id, team_id):
    print(team_id)
    team = TournamentTeam.objects.filter(
        Q(team=team_id) & Q(tournament=tournament_id))
    team.delete()
    messages.success(request, "Team was removed successfully")
    return redirect("panel:confirm-tournament-view")


# Set Tournament Groups
@group_based_access(groups=['it'])
def set_groups(request, tournament_id):
    manage_tournament.generate_tournament(tournament_id)
    return redirect("panel:confirm-tournament-view")

# View every tournament - every user


def view_tournaments(request):
    tournament_list = Tournament.objects.all()

    return render(request, "panel/all-tournaments.html", {"tournament_list": tournament_list})


# View tournament matches - every user + RABC for manage matches

def view_matches(request, tournament_id):
    match_list = TournamentMatch.objects.filter(tournament_id=tournament_id)
    return render(request, "panel/tournament-matches.html", {"match_list": match_list, "access": request.user.groups.filter(name__in=['referee']).exists()})

# View to manage a match


@group_based_access(groups=['referee'])
def manage_match(request, match_id):

    match_data = TournamentMatch.objects.get(match_id=match_id)
    if match_data.match.match_status == Match.MatchStatus.PENDING:
        match_data.match.match_status = Match.MatchStatus.DURING
        match_data.match.user = request.user
        match_data.match.save()

    if request.method == "POST":
        if request.POST.get('finish'):
            team_1_result = request.POST['team_1_result']
            team_2_result = request.POST['team_2_result']
            finish_match.calcualte_match_data(match_data, team_1_result, team_2_result)
            #    return redirect("panel:tournament-list-view")
            #else:
            #    messages.error(request, "Error occured during saving match data")

        if request.POST.get('cancel'):
            match_data.match.team_1_result = 0
            match_data.match.team_2_result = 0
            match_data.match.match_status = Match.MatchStatus.PENDING
            match_data.match.user = None
            match_data.match.save()
            return redirect("panel:tournament-list-view")
        if request.POST.get('save'):
            match_form = MatchForm(request.POST or None)
            if match_form.is_valid():
                match_data.match.team_1_result = request.POST['team_1_result']
                match_data.match.team_2_result = request.POST['team_2_result']
                match_data.match.save()

            else:
                for error in match_form.errors:
                    messages.error(request, error)

    else:
        pass
    
    match_form = MatchForm(instance=match_data.match)
        

    return render(request, "panel/manage-match.html", {"match_form": match_form})


# View to see matches assigned to a referee profile
@group_based_access(groups=['referee'])
def my_matches(request):
    match_list = Match.objects.filter(user = request.user)
    print(match_list)
    return render(request, "panel/my-matches.html", {"match_list" : match_list})
