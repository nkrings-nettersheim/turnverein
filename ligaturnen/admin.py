from django.contrib import admin
from .models import (Vereine, Geraete, Teilnehmer, Ligen, LigaTag, LigaturnenErgebnisse,
                     LigaturnenErgebnisseZwischenLiga, LigaturnenErgebnisseZwischenEinzel)


admin.site.site_header = "Admin Bereich Turnfest Software"

admin.site.register(Vereine)
admin.site.register(Geraete)
admin.site.register(Ligen)
admin.site.register(LigaTag)
admin.site.register(Teilnehmer)
admin.site.register(LigaturnenErgebnisse)
admin.site.register(LigaturnenErgebnisseZwischenLiga)
admin.site.register(LigaturnenErgebnisseZwischenEinzel)
#admin.site.register(Geraete)