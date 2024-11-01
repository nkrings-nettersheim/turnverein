from django.urls import path
from . import views
from .views import index

app_name = 'turnfest'

urlpatterns = [
    path('', index, name='index'),
    path('bezirksturnfest/', views.bezirksturnfest, name='bezirksturnfest'),
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),

    path('vereine_create/', views.VereineCreateView.as_view(), name='vereine_create'),
    path('vereine_list/', views.VereineListView.as_view(), name='vereine_list'),
    path('vereine_detail/<int:pk>/', views.VereineDetailView.as_view(), name='vereine_detail'),
    path('vereine_edit/<int:pk>/', views.VereineUpdateView.as_view(), name='vereine_edit'),
    path('vereine_delete/<int:pk>/', views.VereineDeleteView.as_view(), name='vereine_delete'),
    path('vereine_upload/', views.vereine_upload, name='vereine_upload'),
    path('report_vereine/', views.report_vereine, name='report_vereine'),

    path('teilnehmer_create/', views.TeilnehmerCreateView.as_view(), name='teilnehmer_create'),
    path('teilnehmer_list/', views.TeilnehmerList.as_view(), name='teilnehmer_list'),
    path('teilnehmer_detail/<int:pk>/', views.TeilnehmerDetailView.as_view(), name='teilnehmer_detail'),
    path('teilnehmer_edit/<int:pk>/', views.TeilnehmerUpdateView.as_view(), name='teilnehmer_edit'),
    path('teilnehmer_delete/<int:pk>/', views.TeilnehmerDeleteView.as_view(), name='teilnehmer_delete'),
    path('teilnehmer_upload/', views.teilnehmer_upload, name='teilnehmer_upload'),

    path('ergebnis_erfassen_suche/', views.ergebnis_erfassen_suche, name='ergebnis_erfassen_suche'),
    path('add/ergebnis/', views.add_ergebnis, name='add_ergebnis'),
    path('edit/ergebnis/<id>/', views.edit_ergebnis, name='edit_ergebnis'),
    path('ergebnisse_list/', views.ErgebnisseList.as_view(), name='ergebnisse_list'),

    path('geraetelisten/', views.report_geraetelisten, name='geraetelisten'),
    path('auswertung/', views.report_auswertung, name='auswertung'),
    path('urkunden/', views.report_urkunden_jahrgang, name='urkunden'),
    path('meisterschaften/', views.report_meisterschaften, name='meisterschaften'),
    path('auswertung_vereine/', views.report_auswertung_vereine, name='auswertung_vereine'),

    path('delete_tables/', views.delete_tables_bezirksturnfest, name='delete_tables'),

]
