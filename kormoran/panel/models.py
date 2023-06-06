from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from django.utils.text import slugify
# Create your models here.


class Sport(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "Male"
        FEMALE = "Female"
        MIX = "Mix"

    sport_id = models.AutoField(primary_key=True)
    sport_name = models.CharField(null=False, max_length=100)
    sport_gender = models.CharField(
        null=False, max_length=10, choices=GenderChoices.choices, default=GenderChoices.MIX)
    points_win = models.IntegerField(default=3, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])
    points_lost = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])
    points_draw = models.IntegerField(default=1, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])
    sport_slug = models.SlugField(blank=True, default="")

    def __str__(self) -> str:
        return f"{self.sport_name} {self.sport_gender}"

    def save(self, *args, **kwargs):

        slug_text = f"{self.sport_name} {self.sport_gender}"
        self.sport_slug = slugify(slug_text)
        super(Sport, self).save(*args, **kwargs)


class TempTeam(models.Model):
    temp_id = models.AutoField(primary_key=True)
    temp_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    temp_name = models.CharField(null=False, max_length=100)
    temp_sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.temp_user} {self.temp_name} {self.temp_sport}"


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(null=False, max_length=100)
    team_sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    team_won = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    team_draw = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    team_lost = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    def __str__(self) -> str:
        return f"{self.team_name} {self.team_sport}"


class Match(models.Model):
    class MatchStatus(models.TextChoices):
        COMPLETED = "completed"
        PENDING = "pending"
        DURING = "during"

    sport = models.ForeignKey(Sport, default="", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True, blank=True)
    match_id = models.AutoField(primary_key=True)
    match_name = models.CharField(default="", max_length=100, blank=True)
    team_1 = models.ForeignKey(
        Team, related_name="team_1", on_delete=models.CASCADE)
    team_2 = models.ForeignKey(
        Team, related_name="team_2", on_delete=models.CASCADE)
    match_status = models.CharField(
        null=False, max_length=10, choices=MatchStatus.choices, default=MatchStatus.PENDING)
    team_1_result = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100),
    ])
    team_2_result = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100),
    ])

    def __str__(self) -> str:
        return f"{self.sport} {self.team_1} {self.team_2}"


class TournamentTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)
    selected = models.BooleanField(default=False)
    final_position = models.IntegerField(default=0, validators=[
        MinValueValidator(-1),
        MaxValueValidator(100),
    ])
    ladder_choice = models.IntegerField(default=0, validators=[
        MinValueValidator(-1),
        MaxValueValidator(256)
    ])
    group_choice = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(4)
    ])
    team_won = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    team_lost = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    team_draw = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])

    team_points = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)])

    points_scored = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(300)])

    points_lost = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(300)])
    points_balance = models.IntegerField(default=0, validators=[
        MinValueValidator(-150),
        MaxValueValidator(150)
    ])

    def __str__(self) -> str:
        return f"{self.team} {self.tournament}"


class TournamentMatch(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    tournament = models.ForeignKey("Tournament", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.match} {self.tournament}"


class Tournament(models.Model):
    class TournamentStatus(models.TextChoices):
        PENDING = "pending"
        GROUP_PENDING = "pending_group"
        GROUP = "group"
        GROUP_FINISHED = "finished_group"
        LADDER_PENDING = "pending_ladder"
        LADDER = "ladder"
        COMPLETED = "completed"

    class TournamentType(models.TextChoices):
        GROUP1 = "1gr", "1 Group"
        GROUP2 = "2gr+ldr", "2 Groups + Ladder"
        GROUP3 = "3gr+ldr", "3 Groups + Ladder"
        GROUP4 = "4gr+ldr", "4 Groups + Ladder"
        LADDER = "ldr", "Ladder"

    matches_left = models.IntegerField(default=0, validators=[
        MinValueValidator(0)
    ])
    tournament_id = models.AutoField(primary_key=True)
    tournament_sport = models.ForeignKey(
        Sport, default="", on_delete=models.CASCADE)
    tournament_name = models.CharField(max_length=100, unique=True)
    tournament_status = models.CharField(
        max_length=20, choices=TournamentStatus.choices, default=TournamentStatus.PENDING)
    tournament_type = models.CharField(
        max_length=100, choices=TournamentType.choices, default=TournamentType.GROUP1)

    def __str__(self) -> str:
        return f"{self.tournament_id} {self.tournament_name} {self.tournament_sport}"
