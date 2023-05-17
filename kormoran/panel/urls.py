from django.urls import path

from . import views

app_name = "panel"

urlpatterns = [
    path("", views.index, name="home-view"),
    path("add-team/", views.add_team, name="add-team-view"),
    path("confirm-team/", views.confirm_team, name="confirm-team-view"),
    path("confirm-team/<int:team_id>/<operation>/",
         views.confirm_single, name="confirm-single-view"),
    path("add-sport/", views.add_sport, name="add-sport-view"),
    path("create-tournament/", views.create_tournament,
         name="create-tournament-view"),
    path("add-tournament-teams/<int:tournament_id>/",
         views.add_tournament_teams, name="add-tournament-teams-view"),
    path("confirm-tournament/", views.confirm_tournaments,
         name="confirm-tournament-view"),
    path("set-groups/<int:tournament_id>/",
         views.set_groups, name="set-groups-view"),
    path("remove-tournament-team/<int:tournament_id>/<int:team_id>/",
         views.remove_team, name="remove-tournament-team-view"),
    path("tournaments/", views.view_tournaments, name="tournament-list-view"),
    path("tournament-matches/<int:tournament_id>/",
         views.view_matches, name="tournament-matches-view"),
    path("manage-match/<int:match_id>/",
         views.manage_match, name="manage-match-view"),
    path("my-matches/",
         views.my_matches, name="my-matches-view"),
]
