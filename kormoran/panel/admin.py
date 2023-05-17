from django.contrib import admin

from .models import Sport
from .models import Team, TempTeam, TournamentTeam, TournamentMatch
from .models import Match, Tournament


# Register your models here.


admin.site.register(Sport)
admin.site.register(Team)
admin.site.register(TempTeam)
admin.site.register(TournamentTeam)
admin.site.register(Match)
admin.site.register(Tournament)
admin.site.register(TournamentMatch)

