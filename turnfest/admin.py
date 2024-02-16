from django.contrib import admin
from .models import Riegen, Vereine, Geraete, Medaille, Meisterschaften, Bezirksturnfest, Teilnehmer, \
    BezirksturnfestErgebnisse, Konfiguration


admin.site.site_header = "Admin Bereich Turnfest Software"

admin.site.register(Vereine)
admin.site.register(Geraete)
admin.site.register(Medaille)
admin.site.register(Meisterschaften)
admin.site.register(Bezirksturnfest)
admin.site.register(Teilnehmer)
admin.site.register(Konfiguration)
admin.site.register(Riegen)
admin.site.register(BezirksturnfestErgebnisse)
#admin.site.register(Geraete)