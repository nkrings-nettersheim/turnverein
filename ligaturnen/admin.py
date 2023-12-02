from django.contrib import admin
from .models import Vereine, Geraete, Teilnehmer, Ligen


admin.site.site_header = "Admin Bereich Turnfest Software"

admin.site.register(Vereine)
admin.site.register(Geraete)
admin.site.register(Ligen)
#admin.site.register(Meisterschaften)
#admin.site.register(Bezirksturnfest)
admin.site.register(Teilnehmer)
#admin.site.register(Wettkampfteilnahme)
#admin.site.register(Riegen)
#admin.site.register(BezirksturnfestErgebnisse)
#admin.site.register(Geraete)