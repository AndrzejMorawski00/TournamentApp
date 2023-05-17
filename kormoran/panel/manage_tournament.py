from .models import Tournament, TournamentTeam, TournamentMatch, Match
from random import shuffle

# Generate Groups


def pairs(n):
    return [[a, b] for a in range(n) for b in range(a, n) if a != b]


def generate_tournament_type(form_data):
    if form_data == "2":
        return 
    elif form_data == "3":
        return 
    elif form_data == "4":
        return 
    elif form_data == "5":
        return 
    else:
        return 

def generate_group_number(tournament_string):
    
    if tournament_string == "2gr+ldr":
        return 2
    elif tournament_string == "3gr+ldr":
        return 3
    elif tournament_string == "4gr+ldr":
        return 4
    
    return 1
    

def print_groups(groups):

    counter_1 = 1
    for group in groups:
        print("Group: ", counter_1)
        counter_1 += 1
        counter_2 = 1
        for team in group:
            print("Pos:", counter_2, ".", team)
            counter_2 += 1


def assign_teams(teams,  tournament):
    group_number = generate_group_number(tournament.tournament_type)
    if group_number == 0:
        group_number = 1 # Temp
    group_size = int(round(len(teams) / group_number))
    last_group_size = len(teams) - (group_number - 1) * group_size
    groups = [[] for _ in range(group_number)]

    for i in range(1, group_number + 1):
        chosen_teams = list(teams.filter(group=i))
        shuffle(chosen_teams)
        if i != group_number:
            selected_teams = chosen_teams[0:group_size]
        else:
            selected_teams = chosen_teams[0:last_group_size]
        for team in selected_teams:
            team.selected = True
            team.save()
        groups[i - 1] = list(selected_teams)

    for i in range(1, group_number + 1):
        rest_of_teams = list(teams.filter(selected=False))
        shuffle(rest_of_teams)
        if i != group_number:
            places_left = group_size - len(groups[i - 1])
        else:
            places_left = last_group_size - len(groups[i - 1])
        selected_teams = rest_of_teams[0:places_left]

        for team in selected_teams:
            print(team)
            groups[i - 1].append(team)
            team.selected = True
            team.save()

    save_groups(groups)
    print_groups(groups)
    return groups


def set_false(teams):
    for team in teams:
        team.selected = False
        team.save()


def save_groups(groups):
    for i in range(len(groups)):  # Iterate for groups
        for j in range(len(groups[i])):  # Iterate in single group
            groups[i][j].group = i + 1
            groups[i][j].save()


def reset_groups(teams):
    for team in teams:
        team.group = 0
        team.save()

# Generate Matches in groups:


def generate_match(team_1, team_2, tournament):
    new_match = Match(team_1=team_1.team, team_2=team_2.team,
                      sport=tournament.tournament_sport)
    new_match.save()
    tournament_match = TournamentMatch(
        match=new_match, tournament=tournament)
    tournament_match.save()


def generate_matches(groups, tournament):
    print("Generate Matches")
    for group in groups:
        list_of_pairs = pairs(len(group))
        for p in list_of_pairs:
            generate_match(group[p[0]], group[p[1]], tournament)


def generate_tournament(tournament_id):
    tournament = Tournament.objects.get(tournament_id=tournament_id)

    teams = TournamentTeam.objects.filter(
        tournament=tournament).order_by('-group')
    set_false(teams)
    reset_groups(teams)
    if tournament.tournament_type != "Ladder":
        groups = assign_teams(teams, tournament)
        generate_matches(groups, tournament)
    else:
        pass  # Create Tournament


# Choose Operation:

def choose_operation(tournament_id):
    pass