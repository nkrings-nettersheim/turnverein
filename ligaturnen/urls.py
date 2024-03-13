from django.urls import path
from . import views
from .views import index

app_name = 'ligaturnen'

urlpatterns = [
    #Bereich Homepage
    path('', index, name='index'),
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),
    path('ligawettkampf/', views.ligawettkampf, name='ligawettkampf'),

    #Bereich Vereine
    path('vereine_create/', views.VereineCreateView.as_view(), name='vereine_create'),
    path('vereine_list/', views.VereineListView.as_view(), name='vereine_list'),
    path('vereine_detail/<int:pk>/', views.VereineDetailView.as_view(), name='vereine_detail'),
    path('vereine_edit/<int:pk>/', views.VereineUpdateView.as_view(), name='vereine_edit'),
    path('vereine_delete/<int:pk>/', views.VereineDeleteView.as_view(), name='vereine_delete'),
    path('vereine_upload/', views.vereine_upload, name='vereine_upload'),

    #Bereich Ligen
    path('ligen_create/', views.LigenCreateView.as_view(), name='ligen_create'),
    path('ligen_list/', views.LigenListView.as_view(), name='ligen_list'),
    path('ligen_detail/<int:pk>/', views.LigenDetailView.as_view(), name='ligen_detail'),
    path('ligen_edit/<int:pk>/', views.LigenUpdateView.as_view(), name='ligen_edit'),
    path('ligen_delete/<int:pk>/', views.LigenDeleteView.as_view(), name='ligen_delete'),

    #Bereich Teilnehmer
    path('teilnehmer_create/', views.TeilnehmerCreateView.as_view(), name='teilnehmer_create'),
    path('teilnehmer_list/', views.TeilnehmerList.as_view(), name='teilnehmer_list'),
    path('teilnehmer_detail/<int:pk>/', views.TeilnehmerDetailView.as_view(), name='teilnehmer_detail'),
    path('teilnehmer_edit/<int:pk>/', views.TeilnehmerUpdateView.as_view(), name='teilnehmer_edit'),
    path('teilnehmer_delete/<int:pk>/', views.TeilnehmerDeleteView.as_view(), name='teilnehmer_delete'),
    path('teilnehmer_upload/', views.teilnehmer_upload, name='teilnehmer_upload'),


    #ergebnis erfassen Bereich
    path('ergebnis_erfassen_suche/', views.ergebnis_erfassen_suche, name='ergebnis_erfassen_suche'),
    path('add/ergebnis/', views.add_ergebnis, name='add_ergebnis'),
    path('edit/ergebnis/<id>/', views.edit_ergebnis, name='edit_ergebnis'),
    path('ergebnisse_list/', views.ErgebnisseList.as_view(), name='ergebnisse_list'),

    # Bereich Auswertungen
    path('auswertungeinzel/', views.report_auswertung_einzel, name='auswertungeinzel'),
    path('urkundeeinzel/', views.report_urkunde_einzel, name='urkundeeinzel'),
    path('auswertungmannschaft/', views.report_auswertung_mannschaft, name='auswertungmannschaft'),
    path('urkundemannschaft/', views.report_urkunde_mannschaft, name='urkundemannschaft'),
    path('auswertungvereine/', views.report_auswertung_vereine, name='auswertungvereine'),

    # mix Bereich
    path('download/', views.download_document, name='download'),
    path('geraetelisten/', views.report_geraetelisten, name='geraetelisten'),
    path('meldungen/', views.report_meldungen, name='meldungen'),
    path('tables_delete/', views.ligaturnen_tables_delete, name='tables_delete'),
    path('ligatag_edit/<int:pk>/', views.LigaTagUpdateView.as_view(), name='ligatag_edit'),
    path('check_rules/', views.check_rules, name='check_rules'),

]
