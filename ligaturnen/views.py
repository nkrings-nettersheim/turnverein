import pandas as pd
import io
import logging
import locale

from django.contrib.auth.mixins import PermissionRequiredMixin
from datetime import datetime

from django.conf import settings
from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.http import FileResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission
from reportlab.lib.enums import TA_CENTER

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, Spacer

from turnverein.settings import BASE_DIR

from .models import Vereine, Teilnehmer, Ligen, Geraete, LigaturnenErgebnisse, LigaturnenErgebnisseZwischenLiga, \
    LigaTag, LigaturnenErgebnisseZwischenEinzel, LigaturnenErgebnisseZwischenLigaGesamt, Konfiguration
from .forms import VereinErfassenForm, LigaErfassenForm, TeilnehmerErfassenForm, UploadFileForm, \
    ErgebnisTeilnehmererfassenForm, ErgebnisTeilnehmerSuchen, TablesDeleteForm

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")


@login_required
def index(request):
    return render(request, 'ligaturnen/index.html')


@login_required
def impressum(request):
    return render(request, 'ligaturnen/impressum.html')


@login_required
def datenschutz(request):
    return render(request, 'ligaturnen/datenschutz.html')


@login_required
def ligawettkampf(request):
    teilnehmer_1 = Teilnehmer.objects.filter(teilnehmer_liga_tag="1").count()
    teilnehmer_2 = Teilnehmer.objects.filter(teilnehmer_liga_tag="2").count()

    dashboard = {}
    dashboard["teilnehmer_1"] = teilnehmer_1
    dashboard["teilnehmer_2"] = teilnehmer_2

    request.session['geraet'] = ""
    request.session['teilnehmer'] = ""

    logger.debug(f"User {request.user.id} hat die Startseite des Ligawettkampfs aufgerufen")
    return render(request, 'ligaturnen/ligawettkampf.html', {'dashboard': dashboard})


##########################################################################
# Area Verein create and change
##########################################################################
class VereineCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "ligaturnen.view_vereine"
    model = Vereine
    template_name = "ligaturnen/vereine_create.html"
    form_class = VereinErfassenForm
    success_url = reverse_lazy("ligaturnen:vereine_list")

    def get(self, request, *args, **kwargs):
        logger.info(f"Anlegen Verein gestartet")
        return super().get(request, *args, **kwargs)


class VereineListView(PermissionRequiredMixin, ListView):
    permission_required = "ligaturnen.view_vereine"
    model = Vereine


class VereineDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "ligaturnen.view_vereine"
    model = Vereine


class VereineUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "ligaturnen.change_vereine"
    model = Vereine
    template_name = "ligaturnen/vereine_edit.html"
    fields = '__all__'
    success_url = "/ligaturnen/vereine_list/"


class VereineDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "ligaturnen.change_vereine"
    model = Vereine
    template_name = "ligaturnen/vereine_delete.html"
    success_url = reverse_lazy("ligaturnen:vereine_list")


##########################################################################
# Area Ligen create and change
##########################################################################
class LigenCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "ligaturnen.add_ligen"
    model = Ligen
    template_name = "ligaturnen/ligen_create.html"
    form_class = LigaErfassenForm
    success_url = reverse_lazy("ligaturnen:ligen_list")


class LigenListView(PermissionRequiredMixin, ListView):
    permission_required = "ligaturnen.view_ligen"
    model = Ligen


class LigenDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "ligaturnen.view_ligen"
    model = Ligen


class LigenUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "ligaturnen.change_ligen"
    model = Ligen
    template_name = "ligaturnen/ligen_edit.html"
    fields = '__all__'
    success_url = "/ligaturnen/ligen_list/"


class LigenDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "ligaturnen.change_ligen"
    model = Ligen
    template_name = "ligaturnen/ligen_delete.html"
    success_url = reverse_lazy("ligaturnen:ligen_list")


##########################################################################
# Area Teilnehmer create and change
##########################################################################
class TeilnehmerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "ligaturnen.add_teilnehmer"
    model = Teilnehmer
    template_name = "ligaturnen/teilnehmer_create.html"
    form_class = TeilnehmerErfassenForm
    # fields = '__all__'
    success_url = reverse_lazy("ligaturnen:teilnehmer_list")


class TeilnehmerList(PermissionRequiredMixin, ListView):
    permission_required = "ligaturnen.view_teilnehmer"
    model = Teilnehmer
    ordering = ['teilnehmer_liga_tag', 'teilnehmer_liga', 'teilnehmer_verein', 'teilnehmer_mannschaft',
                'teilnehmer_name', 'teilnehmer_vorname']


class TeilnehmerDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "ligaturnen.view_teilnehmer"
    model = Teilnehmer


class TeilnehmerUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "ligaturnen.change_teilnehmer"
    model = Teilnehmer
    template_name = "ligaturnen/teilnehmer_edit.html"
    # fields = '__all__'
    form_class = TeilnehmerErfassenForm
    success_url = reverse_lazy("ligaturnen:teilnehmer_list")


class TeilnehmerDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "ligaturnen.change_teilnehmer"
    model = Teilnehmer
    template_name = "ligaturnen/teilnehmer_delete.html"
    success_url = reverse_lazy("ligaturnen:teilnehmer_list")


# @permission_required('reports.add_process_report')
@login_required
@permission_required('ligaturnen.add_teilnehmer')
def teilnehmer_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            countdict = handle_uploaded_file(request.FILES['file'])
            request.session['count_positiv'] = str(countdict["count_positiv"])
            request.session['count_negativ'] = str(countdict["count_negativ"])
            logger.info(f"User {request.user.id} hat eine neue Teilnehmerliste hochgeladen")
            if countdict["name_fault"]:
                request.session['name_fault'] = str(countdict["name_fault"])
                form = UploadFileForm()
                return render(request, 'ligaturnen/teilnehmer_upload.html', {'form': form})

            return redirect('/ligaturnen/teilnehmer_list/')
    else:
        request.session['name_fault'] = ""
        form = UploadFileForm()
    return render(request, 'ligaturnen/teilnehmer_upload.html', {'form': form})


def handle_uploaded_file(file):
    # Lese die Daten aus der Excel-Datei
    df = pd.read_excel(file)

    name_fault = ""
    count_positiv = 0
    count_negativ = 0
    # Iteriere durch die Zeilen und speichere die Daten in der Datenbank
    for index, row in df.iterrows():
        counter_geraet = 0
        name_fault = ''

        if row['Sprung'] > 0:
            counter_geraet = counter_geraet + 1
        if row['Minitrampolin'] > 0:
            counter_geraet = counter_geraet + 1
        if row['Reck_Stufenbarren'] > 0:
            counter_geraet = counter_geraet + 1
        if row['Schwebebalken'] > 0:
            counter_geraet = counter_geraet + 1
        if row['Barren'] > 0:
            counter_geraet = counter_geraet + 1
        if row['Boden'] > 0:
            counter_geraet = counter_geraet + 1

        if counter_geraet <=4 :
            Teilnehmer_neu = Teilnehmer(teilnehmer_liga_tag=row['Liga_Tag'],
                                        teilnehmer_name=row['Nachname'],
                                        teilnehmer_vorname=row['Vorname'],
                                        teilnehmer_gender=row['Geschlecht'],
                                        teilnehmer_geburtsjahr=row['Geburtsjahr'],
                                        teilnehmer_verein_id=row['Verein'],
                                        teilnehmer_anwesend="True",
                                        teilnehmer_liga=row['Liga'],
                                        teilnehmer_mannschaft=row['Mannschaft'],
                                        teilnehmer_ak=row['ak'],
                                        teilnehmer_sprung=row['Sprung'],
                                        teilnehmer_mini=row['Minitrampolin'],
                                        teilnehmer_reck_stufenbarren=row['Reck_Stufenbarren'],
                                        teilnehmer_balken=row['Schwebebalken'],
                                        teilnehmer_barren=row['Barren'],
                                        teilnehmer_boden=row['Boden'],
                                        )
            try:
                Teilnehmer_neu.save()
                count_positiv = count_positiv + 1
            except:
                count_negativ = count_negativ + 1
        else:
            name_fault = row['Nachname'] + " "+ row['Vorname']
            countdict = {"count_positiv": count_positiv, "count_negativ": count_negativ, "name_fault": name_fault}
            return countdict

    countdict = {"count_positiv": count_positiv, "count_negativ": count_negativ, "name_fault": name_fault}
    return countdict


##########################################################################
# Area Ligatag change
##########################################################################
class LigaTagUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "ligaturnen.change_ligatag"
    model = LigaTag
    template_name = "ligaturnen/ligatag_edit.html"
    fields = '__all__'
    success_url = "/ligaturnen/ligawettkampf/"


##########################################################################
# Area Download verschiedene Dokumente
##########################################################################
@login_required
def download_document(request):
    if request.method == 'GET':
        file_name = request.GET.get('file_name')
        document_path = settings.MEDIA_ROOT + '/' + str(file_name)
        response = FileResponse(open(document_path, 'rb'), as_attachment=True)
        return response

    return redirect('/ligaturnen/')


##########################################################################
# Area Geräteliste und Mannschaftsübersicht erzeugen
##########################################################################
@login_required
@permission_required('ligaturnen.add_teilnehmer')
def report_geraetelisten(request):
    ligen = Ligen.objects.all()
    geraete = Geraete.objects.all()
    # zunächst provisorisch hier hart codiert
    ligaTag = LigaTag.objects.get(id=1)

    # Definieren Sie die gewünschte Schriftart und laden Sie sie
    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    response = HttpResponse(content_type='application/pdf')
    # inline für Anzeige im Browser; attachment für direkten Download
    response['Content-Disposition'] = 'attachment; filename="Wettkampfliste_Ligaturnen.pdf"'

    # Create the PDF object, using the buffer as its "file."
    pdf = SimpleDocTemplate(response,
                            rightMargin=10,
                            leftMargin=10,
                            topMargin=10,
                            bottomMargin=10,
                            pagesize=A4,
                            )

    # Create styles
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='CenterAlign20',
                              fontName='DejaVuSans-Bold',
                              fontSize=20,
                              alignment=TA_CENTER))

    styles.add(ParagraphStyle(name='CenterAlign14',
                              fontName='DejaVuSans-Bold',
                              fontSize=14,
                              alignment=TA_CENTER))

    normal_style = styles['Normal']
    heading_style = styles['Heading1']
    heading_style.alignment = TA_CENTER

    # Create a list to store the content for the PDF
    content = []
    for geraet in geraete:
        for liga in ligen:

            teilnehmer_alle = []

            if geraet.geraet_db_name == "teilnehmer_sprung":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_sprung__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_sprung'
                                                      ).order_by('teilnehmer_sprung')

            elif geraet.geraet_db_name == "teilnehmer_mini":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_mini__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_mini'
                                                      ).order_by('teilnehmer_mini')

            elif geraet.geraet_db_name == "teilnehmer_reck_stufenbarren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_reck_stufenbarren__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_reck_stufenbarren'
                                                      ).order_by('teilnehmer_reck_stufenbarren')

            elif geraet.geraet_db_name == "teilnehmer_balken":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_balken__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_balken'
                                                      ).order_by('teilnehmer_balken')

            elif geraet.geraet_db_name == "teilnehmer_barren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_barren__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_barren'
                                                      ).order_by('teilnehmer_barren')

            elif geraet.geraet_db_name == "teilnehmer_boden":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_boden__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_boden'
                                                      ).order_by('teilnehmer_boden')

            if teilnehmer_alle:
                content.append(Paragraph('Ligaturnen ' + str(ligaTag.ligajahr), styles['CenterAlign20']))
                content.append(Spacer(1, 4))

                content.append(Paragraph(
                    "____________________________________________________________________________________________________",
                    normal_style))
                content.append(Spacer(1, 4))

                content.append(Paragraph(liga.liga + "-Liga " + geraet.geraet_name + " Ligatag: " + str(ligaTag),
                                         styles['CenterAlign14']))
                content.append(Spacer(1, 12))

                headers = ['Start-Nr.', 'Nachname', 'Vorname', 'Verein', 'Jahrgang', 'Meldung', 'A-Note*', 'B-Note']
                table_data = [headers] + [list(row) + [''] * (len(headers) - len(row)) for row in teilnehmer_alle]
                if table_data:
                    t = Table(table_data)
                    content.append(t)
                    content.append(Spacer(1, 4))
                    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.white),
                                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('FONT', (0, 0), (-1, -1), 'DejaVuSans'),
                                           ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                                           ('ALIGN', (5, 0), (5, -1), 'CENTER')
                                           ]))

                content.append(Paragraph(
                    "*: A-Note nur eintragen, wenn es eine Änderung zur Meldung gegeben hat!", normal_style))

                content.append(PageBreak())

    pdf.build(content)

    return response


@login_required
@permission_required('ligaturnen.add_teilnehmer')
def report_meldungen(request):
    # Definieren Sie die gewünschte Schriftart und laden Sie sie
    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Holen der Seitenabmessung
    breite, hoehe = A4

    configuration = Konfiguration.objects.get(id=1)
    ligen = Ligen.objects.all()
    vereine = Vereine.objects.all()
    ligaTag = LigaTag.objects.get(id=1)
    mannschaften = [1, 2, 3]

    for verein in vereine:
        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Ligawettkampf " + str(configuration.liga_jahr) + " Meldungen" + " Ligatag: " + str(ligaTag))
        h = h + 0.2

        p.setFont('DejaVuSans-Bold', 11)
        p.drawCentredString(breite / 2, hoehe - (h * cm),
            "____________________________________________________________________________________________________")
        h = h + 0.7

        p.setFont('DejaVuSans-Bold', 14)
        p.drawCentredString(breite / 2, hoehe - (h * cm), verein.verein_name_kurz)

        for liga in ligen:
            h = h + 0.5
            p.setFillColorRGB(0, 0, 0)  # choose your font colour
            p.setFont('DejaVuSans-Bold', 12)
            p.drawCentredString(breite / 2, hoehe - (h * cm), str(liga) + "-Liga")

            for mannschaft in mannschaften:
                meldungen = Teilnehmer.objects.filter(teilnehmer_verein=verein,
                                                      teilnehmer_liga=liga,
                                                      teilnehmer_mannschaft=mannschaft,
                                                      teilnehmer_ak=False,
                                                      teilnehmer_anwesend=True,
                                                      teilnehmer_liga_tag=ligaTag).order_by('teilnehmer_name')

                if meldungen:
                    h = h + 0.5
                    p.setFillColorRGB(0, 0, 0)  # choose your font colour
                    p.setFont('DejaVuSans', 10)
                    p.drawCentredString(breite / 2, hoehe - (h * cm), str(mannschaft) + ". Mannschaft")

                    h = h + 0.5
                    p.drawString(6 * cm, hoehe - (h * cm), 'Startnr.')
                    p.drawString(8 * cm, hoehe - (h * cm),'Turnerin/Turner')
                    p.drawString(12 * cm, hoehe - (h * cm), 'Jahrgang')
                    p.drawString(15 * cm, hoehe - (h * cm), 'Geschlecht')
                    h = h + 0.5
                    z = 1

                    for meldung in meldungen:
                        if meldungen.count() > 6:
                            p.setFillColorRGB(1, 0.2, 0.33)  # choose your font colour
                        p.setFont('DejaVuSans', 10)
                        p.drawString(6 * cm, hoehe - (h * cm), str(meldung.id))
                        p.drawString(8 * cm, hoehe - (h * cm), str(meldung.teilnehmer_vorname) + " " + str(meldung.teilnehmer_name))
                        p.drawString(12 * cm, hoehe - (h * cm), str(
                                            datetime.strptime(str(meldung.teilnehmer_geburtsjahr), "%Y-%m-%d").year))
                        p.drawString(15 * cm, hoehe - (h * cm), str(meldung.teilnehmer_gender))

                        h = h + 0.5
                        if h > 26:
                            current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
                            p.setFillColorRGB(0, 0, 0)  # choose your font colour
                            p.setFont('DejaVuSans', 8)
                            p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))
                            h = 2
                            p.showPage()

        current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
        p.setFont('DejaVuSans', 8)
        p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

        p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="Meldungen.pdf")

##########################################################################
# Area Ergebnisse erfassen
##########################################################################
@login_required
@permission_required('ligaturnen.view_ligaturnenergebnisse')
def ergebnis_erfassen_suche(request):

    if request.method == "POST":
        startnummer = request.POST['startnummer']
        geraete_id = request.POST['geraet']
        ligatag = LigaTag.objects.get(id=1)
        request.session['startnummer'] = str(startnummer)
        request.session['geraet'] = str(geraete_id)
        request.session['ligatag'] = str(ligatag)

        try:
            teilnehmer = Teilnehmer.objects.get(id=startnummer, teilnehmer_liga_tag=ligatag.ligatag)
            try:
                ergebnis = LigaturnenErgebnisse.objects.get(ergebnis_teilnehmer=startnummer)
                return redirect("/ligaturnen/edit/ergebnis/" + str(ergebnis.id) + '/')
            except:
                return redirect("/ligaturnen/add/ergebnis" + "/")

        except:
            form = ErgebnisTeilnehmerSuchen()
            form.startnummerfalse = True
            return render(request, 'ligaturnen/ergebnis_erfassen_suche.html', {'form': form})


    else:
        if request.session['geraet']:
            geraet_option = request.session['geraet']
        else:
            geraet_option = ""

        if request.session['teilnehmer']:
            teilnehmer_id = request.session['teilnehmer']
        else:
            teilnehmer_id = ""

        if teilnehmer_id:
            ergebnis = LigaturnenErgebnisse.objects.get(id=teilnehmer_id)
        else:
            ergebnis = ""
        form = ErgebnisTeilnehmerSuchen()
        form.geraet_option = geraet_option

    return render(request, 'ligaturnen/ergebnis_erfassen_suche.html', {'form': form, 'ergebnis': ergebnis})


@login_required
@permission_required('ligaturnen.add_ligaturnenergebnisse')
def add_ergebnis(request):
    if request.method == "POST":
        form = ErgebnisTeilnehmererfassenForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            request.session['teilnehmer'] = str(item.id)
            return redirect('/ligaturnen/ergebnis_erfassen_suche/')
        else:
            for field in form:
                print("Field Error:", field.name, field.errors)
    else:
        teilnehmer = Teilnehmer.objects.get(id=request.session['startnummer'])
        ligatag = LigaTag.objects.get(id=1)

        form = ErgebnisTeilnehmererfassenForm()
        form.turnerin = teilnehmer.teilnehmer_name + " " + teilnehmer.teilnehmer_vorname
        form.teilnehmer_id = teilnehmer.id
        form.sprung = teilnehmer.teilnehmer_sprung
        form.mini = teilnehmer.teilnehmer_mini
        form.reck = teilnehmer.teilnehmer_reck_stufenbarren
        form.balken = teilnehmer.teilnehmer_balken
        form.barren = teilnehmer.teilnehmer_barren
        form.boden = teilnehmer.teilnehmer_boden
        form.geraet = request.session['geraet']
        form.ligatag = ligatag
        form.add = True  # Damit im Formular die hidden Felder eingeblendet werden
    return render(request, 'ligaturnen/ergebnis_erfassen.html', {'form': form})


@login_required
@permission_required('ligaturnen.add_ligaturnenergebnisse')
def edit_ergebnis(request, id=None):
    item = get_object_or_404(LigaturnenErgebnisse, id=id)
    anzahl_geraete = 0
    if item.ergebnis_sprung_s > 0:
        anzahl_geraete = anzahl_geraete + 1
    if item.ergebnis_reck_s > 0:
        anzahl_geraete = anzahl_geraete + 1
    if item.ergebnis_mini_s > 0:
        anzahl_geraete = anzahl_geraete + 1
    if item.ergebnis_balken_s > 0:
        anzahl_geraete = anzahl_geraete + 1
    if item.ergebnis_barren_s > 0:
        anzahl_geraete = anzahl_geraete + 1
    if item.ergebnis_boden_s > 0:
        anzahl_geraete = anzahl_geraete + 1

    form = ErgebnisTeilnehmererfassenForm(request.POST or None, instance=item)

    # if anzahl_geraete < 5:
    if form.is_valid():
        form.save()
        request.session['teilnehmer'] = id
        return redirect('/ligaturnen/ergebnis_erfassen_suche/')

    ligatag = LigaTag.objects.get(id=1)
    form.id = item.id
    form.turnerin = item.ergebnis_teilnehmer
    form.teilnehmer_id = item.ergebnis_teilnehmer.id
    form.sprung = item.ergebnis_teilnehmer.teilnehmer_sprung
    form.mini = item.ergebnis_teilnehmer.teilnehmer_mini
    form.reck = item.ergebnis_teilnehmer.teilnehmer_reck_stufenbarren
    form.balken = item.ergebnis_teilnehmer.teilnehmer_balken
    form.barren = item.ergebnis_teilnehmer.teilnehmer_barren
    form.boden = item.ergebnis_teilnehmer.teilnehmer_boden
    form.geraet = request.session['geraet']
    form.ligatag = ligatag
    return render(request, 'ligaturnen/ergebnis_erfassen.html', {'form': form})


class ErgebnisseList(PermissionRequiredMixin, ListView):
    permission_required = "ligaturnen.add_ligaturnenergebnisse"
    model = LigaturnenErgebnisse
    ordering = ['ergebnis_teilnehmer__teilnehmer_liga_tag',
                'ergebnis_teilnehmer__teilnehmer_liga',
                'ergebnis_teilnehmer__teilnehmer_verein',
                'ergebnis_teilnehmer__teilnehmer_mannschaft',
                'ergebnis_teilnehmer__teilnehmer_name',
                'ergebnis_teilnehmer__teilnehmer_vorname']


##########################################################################
# Area Auswertung Ligaturnen Mannschaften
##########################################################################
@login_required
@permission_required('ligaturnen.add_ligaturnenergebnisse')
def report_auswertung_mannschaft(request):
    ligen = Ligen.objects.all()
    vereine = Vereine.objects.all()
    ligaTag = LigaTag.objects.get(id=1)
    configuration = Konfiguration.objects.get(id=1)

    gender = ['w', 'm']
    ligatage = ['1', '2']

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Holen der Seitenabmessung
    breite, hoehe = A4

    # Ermittlung der Ergebnisse für die Mannschaften und speichern in der Zwischentabelle
    count_zwischenergebnisse = LigaturnenErgebnisseZwischenLiga.objects.all().delete()
    count_zwischenergebnisse_gesamt = LigaturnenErgebnisseZwischenLigaGesamt.objects.all().delete()

    for liga in ligen:
        for verein in vereine:
            for mannschaft in range(1, 3):
                for gen in gender:
                    for ligatag in ligatage:
                        erg_zwischen = []
                        erg_summe = 0

                        try:
                            erg_sprung = LigaturnenErgebnisse.objects.filter(
                                ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                                ergebnis_teilnehmer__teilnehmer_verein=verein,
                                ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                                ergebnis_teilnehmer__teilnehmer_ak=0,
                                ergebnis_teilnehmer__teilnehmer_gender=gen,
                                ergebnis_ligatag=ligatag
                            ).order_by('-ergebnis_sprung_s')[:3]
                            if erg_sprung:
                                for erg in erg_sprung:
                                    #print(f"Liga: {liga}; Verein: {verein}; Mannschaft: {mannschaft}; Gender: {gen}; ligatag: {ligatag}; Ergebnis Sprung: {erg.ergebnis_sprung_s}")
                                    erg_zwischen.append(erg.ergebnis_sprung_s)
                        except:
                            pass

                        try:
                            erg_mini = LigaturnenErgebnisse.objects.filter(
                                ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                                ergebnis_teilnehmer__teilnehmer_verein=verein,
                                ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                                ergebnis_teilnehmer__teilnehmer_ak=0,
                                ergebnis_teilnehmer__teilnehmer_gender=gen,
                                ergebnis_ligatag = ligatag
                            ).order_by('-ergebnis_mini_s')[:3]
                            if erg_mini:
                                for erg in erg_mini:
                                    #print(f"Liga: {liga}; Verein: {verein}; Mannschaft: {mannschaft}; Gender: {gen}; ligatag: {ligatag}; Ergebnis Mini: {erg.ergebnis_mini_s}")
                                    erg_zwischen.append(erg.ergebnis_mini_s)
                        except:
                            pass

                        try:
                            erg_reck = LigaturnenErgebnisse.objects.filter(
                                ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                                ergebnis_teilnehmer__teilnehmer_verein=verein,
                                ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                                ergebnis_teilnehmer__teilnehmer_ak=0,
                                ergebnis_teilnehmer__teilnehmer_gender=gen,
                                ergebnis_ligatag = ligatag
                            ).order_by('-ergebnis_reck_s')[:3]
                            if erg_reck:
                                for erg in erg_reck:
                                    #print(f"Liga: {liga}; Verein: {verein}; Mannschaft: {mannschaft}; Gender: {gen}; ligatag: {ligatag}; Ergebnis Reck: {erg.ergebnis_reck_s}")
                                    erg_zwischen.append(erg.ergebnis_reck_s)
                        except:
                            pass

                        try:
                            erg_barren = LigaturnenErgebnisse.objects.filter(
                                ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                                ergebnis_teilnehmer__teilnehmer_verein=verein,
                                ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                                ergebnis_teilnehmer__teilnehmer_ak=0,
                                ergebnis_teilnehmer__teilnehmer_gender=gen,
                                ergebnis_ligatag = ligatag
                            ).order_by('-ergebnis_barren_s')[:3]
                            if erg_barren:
                                for erg in erg_barren:
                                    #print(f"Liga: {liga}; Verein: {verein}; Mannschaft: {mannschaft}; Gender: {gen}; ligatag: {ligatag}; Ergebnis Barren: {erg.ergebnis_barren_s}")
                                    erg_zwischen.append(erg.ergebnis_barren_s)
                        except:
                            pass

                        try:
                            erg_balken = LigaturnenErgebnisse.objects.filter(
                                ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                                ergebnis_teilnehmer__teilnehmer_verein=verein,
                                ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                                ergebnis_teilnehmer__teilnehmer_ak=0,
                                ergebnis_teilnehmer__teilnehmer_gender=gen,
                                ergebnis_ligatag = ligatag
                            ).order_by('-ergebnis_balken_s')[:3]
                            if erg_balken:
                                for erg in erg_balken:
                                    #print(f"Liga: {liga}; Verein: {verein}; Mannschaft: {mannschaft}; Gender: {gen}; ligatag: {ligatag}; Ergebnis Balken: {erg.ergebnis_balken_s}")
                                    erg_zwischen.append(erg.ergebnis_balken_s)
                        except:
                            pass
                        try:
                            erg_boden = LigaturnenErgebnisse.objects.filter(
                                ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                                ergebnis_teilnehmer__teilnehmer_verein=verein,
                                ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                                ergebnis_teilnehmer__teilnehmer_ak=0,
                                ergebnis_teilnehmer__teilnehmer_gender=gen,
                                ergebnis_ligatag = ligatag
                            ).order_by('-ergebnis_boden_s')[:3]
                            if erg_boden:
                                for erg in erg_boden:
                                    #print(f"Liga: {liga}; Verein: {verein}; Mannschaft: {mannschaft}; Gender: {gen}; ligatag: {ligatag}; Ergebnis boden: {erg.ergebnis_boden_s}")
                                    erg_zwischen.append(erg.ergebnis_boden_s)
                        except:
                            pass

                        # sortieren des List Objekts:
                        erg_zwischen.sort(reverse=True)
                        #if erg_zwischen:
                            #print(f"Ergebnis sortiert: {erg_zwischen}")

                        if len(erg_zwischen) >= 12:
                            anzahl = 12
                        else:
                            anzahl = len(erg_zwischen)

                        for i in range(anzahl):
                            erg_summe = erg_summe + erg_zwischen[i]


                        if erg_summe > 0:
                            print(f"Ergebnis Summe: {erg_summe} Ligatag: {ligatag}")
                            mannschaftergebnis = LigaturnenErgebnisseZwischenLiga(
                                liga=liga,
                                verein=verein,
                                mannschaft=mannschaft,
                                gender=gen,
                                ligatag=ligatag,
                                ergebnis_summe=erg_summe
                            )

                            try:
                                mannschaftergebnis.save()
                            except:
                                print(f"Mannschftsergebnis konnte nicht angelegt werden")

    for liga in ligen:
        for verein in vereine:
            for mannschaft in range(1, 3):
                for gen in gender:
                    erg_summe = 0

                    try:
                        ergebnis = LigaturnenErgebnisseZwischenLiga.objects.filter(
                            liga=liga,
                            verein=verein,
                            mannschaft=mannschaft,
                            gender=gen,
                        )
                        if ergebnis:
                            for erg in ergebnis:
                                print(f"{erg.ergebnis_summe}")
                                erg_summe = erg_summe + erg.ergebnis_summe

                    except:
                        print("There was an error inside save")

                    #print(f"ERgebnis Gesamt Summe: {erg_summe}")
                    if erg_summe > 0:
                        mannschaftergebnisgesamt = LigaturnenErgebnisseZwischenLigaGesamt(
                            liga=liga,
                            verein=verein,
                            mannschaft=mannschaft,
                            gender=gen,
                            ergebnis_summe=erg_summe
                        )

                        try:
                            mannschaftergebnisgesamt.save()
                        except:
                            print("There was an error inside Save mannschaftsergebnisgesamt")

    for gen in gender:
        for liga in ligen:

            ergebnisse_gesamt = LigaturnenErgebnisseZwischenLigaGesamt.objects.filter(liga=liga,
                                                                               gender=gen
                                                                               ).order_by('-ergebnis_summe')
            if ergebnisse_gesamt:
                h = 1
                p.setFont('DejaVuSans-Bold', 24)
                p.drawCentredString(breite / 2, hoehe - (h * cm), "Ligawettkampf " + str(configuration.liga_jahr))
                h = h + 1
                p.setFont('DejaVuSans-Bold', 18)
                p.drawCentredString(breite / 2, hoehe - (h * cm),
                                    "Ergebnisliste Ligaturnen: Mannschaft")
                h = h + 0.8
                p.setFont('DejaVuSans-Bold', 14)
                if gen == 'w':
                    gen_long = 'weiblich'
                else:
                    gen_long = 'männlich'

                p.drawCentredString(breite / 2, hoehe - (h * cm), liga.liga + "-Liga, " + gen_long)

                # Berechnung Tag 1
                ergebnisse = LigaturnenErgebnisseZwischenLiga.objects.filter(liga=liga,
                                                                             gender=gen,
                                                                             ligatag=1
                                                                             ).order_by('-ergebnis_summe')

                if ergebnisse:
                    h = h + 1

                    p.setFont('DejaVuSans', 8)

                    p.setFillGray(0.75)
                    p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
                    p.setFillGray(0.0)
                    p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Mannschaftswertung 1. Wettkampftag')

                    h = h + 0.5
                    p.setFillGray(0.0)
                    p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Rang')
                    p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Mannschaft')
                    p.drawString(4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
                    p.drawString(18.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')

                    h = h + 0.25
                    hilfsrang = 0
                    rang = 1
                    ergebnis_summe_vorheriger = 0
                    for ergebnis in ergebnisse:
                        if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                            hilfsrang = hilfsrang + 1
                            rang = rang - 1
                            p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                            rang = rang + 1
                        else:
                            if hilfsrang > 0:
                                rang = rang + hilfsrang
                            p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                            rang = rang + 1
                            hilfsrang = 0

                        p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.mannschaft) + ". Mannschaft")
                        p.drawString(4.0 * cm, hoehe - (h * cm), str(ergebnis.verein))
                        p.drawString(18.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))
                        ergebnis_summe_vorheriger = ergebnis.ergebnis_summe
                        h = h + 0.5


                #Berechnung Tag 2
                ergebnisse = LigaturnenErgebnisseZwischenLiga.objects.filter(liga=liga,
                                                                             gender=gen,
                                                                             ligatag=2
                                                                             ).order_by('-ergebnis_summe')

                if ergebnisse:
                    h = h + 1

                    p.setFont('DejaVuSans', 8)

                    p.setFillGray(0.75)
                    p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
                    p.setFillGray(0.0)
                    p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Mannschaftswertung 2. Wettkampftag')

                    h = h + 0.5
                    p.setFillGray(0.0)
                    p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Rang')
                    p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Mannschaft')
                    p.drawString(4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
                    p.drawString(18.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')

                    h = h + 0.25
                    hilfsrang = 0
                    rang = 1
                    ergebnis_summe_vorheriger = 0
                    for ergebnis in ergebnisse:
                        if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                            hilfsrang = hilfsrang + 1
                            rang = rang - 1
                            p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                            rang = rang + 1
                        else:
                            if hilfsrang > 0:
                                rang = rang + hilfsrang
                            p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                            rang = rang + 1
                            hilfsrang = 0

                        p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.mannschaft) + ". Mannschaft")
                        p.drawString(4.0 * cm, hoehe - (h * cm), str(ergebnis.verein))
                        p.drawString(18.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))
                        ergebnis_summe_vorheriger = ergebnis.ergebnis_summe
                        h = h + 0.5


                if ergebnisse_gesamt:
                    h = h + 1

                    p.setFont('DejaVuSans', 8)

                    p.setFillGray(0.75)
                    p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
                    p.setFillGray(0.0)
                    p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamtergebnis')

                    h = h + 0.5
                    p.setFillGray(0.0)
                    p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Rang')
                    p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Mannschaft')
                    p.drawString(4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
                    p.drawString(18.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')

                    h = h + 0.25
                    hilfsrang = 0
                    rang = 1
                    ergebnis_summe_vorheriger = 0
                    for ergebnis in ergebnisse_gesamt:
                        if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                            hilfsrang = hilfsrang + 1
                            rang = rang - 1
                            p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                            rang = rang + 1
                        else:
                            if hilfsrang > 1:
                                rang = rang + hilfsrang
                            p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                            #rang = rang + 1
                            hilfsrang = 0

                        p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.mannschaft) + ". Mannschaft")
                        p.drawString(4.0 * cm, hoehe - (h * cm), str(ergebnis.verein))
                        p.drawString(18.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))
                        ergebnis_summe_vorheriger = ergebnis.ergebnis_summe
                        h = h + 0.5
                        rang = rang + 1

                current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
                p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

                p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Ergebnislisten_Ligaturnen_Mannschaft.pdf")


##########################################################################
# Area Auswertung Ligaturnen Einzelturnerinnen
##########################################################################
@login_required
@permission_required('ligaturnen.add_ligaturnenergebnisse')
def report_auswertung_einzel(request):
    ligen = Ligen.objects.all()
    ligaTag = LigaTag.objects.get(id=1)
    configuration = Konfiguration.objects.get(id=1)

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Holen der Seitenabmessung
    breite, hoehe = A4

    count_zwischenergebnisse = LigaturnenErgebnisseZwischenEinzel.objects.all().delete()

    gender = ['w', 'm']
    for gen in gender:

        teilnehmer_group = Teilnehmer.objects.filter(teilnehmer_gender=gen).order_by('teilnehmer_name',
                                                                                     'teilnehmer_vorname',
                                                                                     'teilnehmer_verein',
                                                                                     'teilnehmer_geburtsjahr',
                                                                                     'teilnehmer_gender')

        teilnehmer_alias_1 = ""
        sprung_zwischen = 0
        mini_zwischen = 0
        reck_zwischen = 0
        balken_zwischen = 0
        barren_zwischen = 0
        boden_zwischen = 0

        for teilnehmer in teilnehmer_group:

            teilnehmer_alias_2 = (f"{teilnehmer.teilnehmer_name}"
                                  f"{teilnehmer.teilnehmer_vorname}"
                                  f"{teilnehmer.teilnehmer_verein}"
                                  f"{teilnehmer.teilnehmer_geburtsjahr}"
                                  f"{teilnehmer.teilnehmer_gender}")

            if teilnehmer_alias_2 == teilnehmer_alias_1:
                try:
                    ergebnis = LigaturnenErgebnisse.objects.get(ergebnis_teilnehmer=teilnehmer.id)
                    if ergebnis:
                        sprung_zwischen = ergebnis.ergebnis_sprung_s + sprung_zwischen
                        mini_zwischen = ergebnis.ergebnis_mini_s + mini_zwischen
                        reck_zwischen = ergebnis.ergebnis_reck_s + reck_zwischen
                        balken_zwischen = ergebnis.ergebnis_balken_s + balken_zwischen
                        barren_zwischen = ergebnis.ergebnis_barren_s + barren_zwischen
                        boden_zwischen = ergebnis.ergebnis_boden_s + boden_zwischen
                        teilnehmer_alias_1 = teilnehmer_alias_2
                except:
                    logger.info("An exception occurred")
            else:
                sprung_zwischen = 0
                mini_zwischen = 0
                reck_zwischen = 0
                balken_zwischen = 0
                barren_zwischen = 0
                boden_zwischen = 0
                try:
                    ergebnis = LigaturnenErgebnisse.objects.get(ergebnis_teilnehmer=teilnehmer.id)
                    if ergebnis:
                        sprung_zwischen = ergebnis.ergebnis_sprung_s + sprung_zwischen
                        mini_zwischen = ergebnis.ergebnis_mini_s + mini_zwischen
                        reck_zwischen = ergebnis.ergebnis_reck_s + reck_zwischen
                        balken_zwischen = ergebnis.ergebnis_balken_s + balken_zwischen
                        barren_zwischen = ergebnis.ergebnis_barren_s + barren_zwischen
                        boden_zwischen = ergebnis.ergebnis_boden_s + boden_zwischen
                        teilnehmer_alias_1 = teilnehmer_alias_2
                except:
                    logger.info("An exception occurred")

            summe_zwischen = sprung_zwischen + mini_zwischen + reck_zwischen + balken_zwischen + barren_zwischen + boden_zwischen
            if summe_zwischen > 0:
                obj, created = LigaturnenErgebnisseZwischenEinzel.objects.update_or_create(
                    teilnehmer_name=teilnehmer.teilnehmer_name,
                    teilnehmer_vorname=teilnehmer.teilnehmer_vorname,
                    teilnehmer_geburtsjahr=teilnehmer.teilnehmer_geburtsjahr,
                    teilnehmer_gender=teilnehmer.teilnehmer_gender,
                    teilnehmer_liga=teilnehmer.teilnehmer_liga,
                    teilnehmer_verein=teilnehmer.teilnehmer_verein,
                    defaults={"ergebnis_sprung_s": sprung_zwischen,
                              "ergebnis_mini_s": mini_zwischen,
                              "ergebnis_reck_s": reck_zwischen,
                              "ergebnis_balken_s": balken_zwischen,
                              "ergebnis_barren_s": barren_zwischen,
                              "ergebnis_boden_s": boden_zwischen,
                              "ergebnis_summe": summe_zwischen
                              }
                )

    for gen in gender:
        for liga in ligen:

            h = 1
            p.setFont('DejaVuSans-Bold', 24)
            p.drawCentredString(breite / 2, hoehe - (h * cm), "Ligawettkampf " + str(configuration.liga_jahr))
            h = h + 1
            p.setFont('DejaVuSans-Bold', 18)
            p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Einzelwertung")
            h = h + 0.8
            p.setFont('DejaVuSans-Bold', 14)
            if gen == 'w':
                gen_long = 'weiblich'
            else:
                gen_long = 'männlich'

            p.drawCentredString(breite / 2, hoehe - (h * cm), liga.liga + "-Liga, " + gen_long)

            ergebnisse = LigaturnenErgebnisse.objects.filter(
                ergebnis_teilnehmer__teilnehmer_gender=gen,
                ergebnis_teilnehmer__teilnehmer_liga=liga,
                ergebnis_ligatag=1
            ).order_by('-ergebnis_summe')

            if ergebnisse:

                p.setFont('DejaVuSans', 8)

                h = h + 1
                p.setFillGray(0.75)
                p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
                p.setFillGray(0.0)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Einzelauswertung 1. Wettkampftag')

                p.setFont('DejaVuSans', 8)

                h = h + 0.5

                p.setFillGray(0.0)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Rang')
                p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
                p.drawString(5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
                p.drawString(8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
                p.drawString(9.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
                p.drawString(11.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
                p.drawString(12.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
                p.drawString(14.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
                p.drawString(16.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
                p.drawString(17.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')

                rang = 1
                hilfsrang = 0
                ergebnis_summe_vorheriger = 0
                h = h + 0.3

                for ergebnis in ergebnisse:

                    if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                        hilfsrang = hilfsrang + 1
                        rang = rang - 1
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                        rang = rang + 1
                    else:
                        if hilfsrang > 0:
                            rang = rang + hilfsrang
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                        rang = rang + 1
                        hilfsrang = 0

                    p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_name) + " " +
                                 str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname))
                    p.drawString(5.0 * cm, hoehe - (h * cm),
                                 str(ergebnis.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))
                    p.drawString(8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
                    p.drawString(9.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
                    p.drawString(11.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
                    p.drawString(12.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
                    p.drawString(14.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
                    p.drawString(16.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
                    p.drawString(17.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))
                    ergebnis_summe_vorheriger = ergebnis.ergebnis_summe

                    h = h + 0.5
                    if h > 28:
                        p.showPage()
                        h = 1
                        p.setFont('DejaVuSans', 8)

            ergebnisse = LigaturnenErgebnisse.objects.filter(
                ergebnis_teilnehmer__teilnehmer_gender=gen,
                ergebnis_teilnehmer__teilnehmer_liga=liga,
                ergebnis_ligatag=2
            ).order_by('-ergebnis_summe')

            if ergebnisse:

                p.setFont('DejaVuSans', 8)

                h = h + 1
                p.setFillGray(0.75)
                p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
                p.setFillGray(0.0)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Einzelauswertung 2. Wettkampftag')

                p.setFont('DejaVuSans', 8)

                h = h + 0.5

                p.setFillGray(0.0)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Rang')
                p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
                p.drawString(5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
                p.drawString(8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
                p.drawString(9.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
                p.drawString(11.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
                p.drawString(12.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
                p.drawString(14.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
                p.drawString(16.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
                p.drawString(17.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')

                hilfsrang = 0
                rang = 1
                ergebnis_summe_vorheriger = 0
                h = h + 0.3

                for ergebnis in ergebnisse:

                    if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                        hilfsrang = hilfsrang + 1
                        rang = rang - 1
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                        rang = rang + 1
                    else:
                        if hilfsrang > 0:
                            rang = rang + hilfsrang
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                        rang = rang + 1
                        hilfsrang = 0


                    p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_name) + " " +
                                 str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname))
                    p.drawString(5.0 * cm, hoehe - (h * cm),
                                 str(ergebnis.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))
                    p.drawString(8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
                    p.drawString(9.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
                    p.drawString(11.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
                    p.drawString(12.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
                    p.drawString(14.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
                    p.drawString(16.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
                    p.drawString(17.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))
                    ergebnis_summe_vorheriger = ergebnis.ergebnis_summe

                    h = h + 0.5
                    if h > 28:
                        p.showPage()
                        h = 1
                        p.setFont('DejaVuSans', 8)

            ergebnisse = LigaturnenErgebnisseZwischenEinzel.objects.filter(
                teilnehmer_gender=gen,
                teilnehmer_liga=liga).order_by('-ergebnis_summe')

            if ergebnisse:
                h = h + 1

                p.setFont('DejaVuSans', 8)

                p.setFillGray(0.75)
                p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
                p.setFillGray(0.0)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Einzelauswertung Gesamtergebnis')

                p.setFont('DejaVuSans', 8)

                h = h + 0.5

                p.setFillGray(0.0)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Rang')
                p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
                p.drawString(5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
                p.drawString(8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
                p.drawString(9.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
                p.drawString(11.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
                p.drawString(12.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
                p.drawString(14.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
                p.drawString(16.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
                p.drawString(17.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')

                hilfsrang = 0
                rang = 1
                ergebnis_summe_vorheriger = 0
                h = h + 0.3
                for ergebnis in ergebnisse:

                    if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                        hilfsrang = hilfsrang + 1
                        rang = rang - 1
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                        rang = rang + 1
                    else:
                        if hilfsrang > 0:
                            rang = rang + hilfsrang
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                        rang = rang + 1
                        hilfsrang = 0

                    p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_name) + " " +
                                 str(ergebnis.teilnehmer_vorname))
                    p.drawString(5.0 * cm, hoehe - (h * cm),
                                 str(ergebnis.teilnehmer_verein.verein_name_kurz))
                    p.drawString(8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
                    p.drawString(9.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
                    p.drawString(11.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
                    p.drawString(12.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
                    p.drawString(14.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
                    p.drawString(16.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
                    p.drawString(17.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))
                    ergebnis_summe_vorheriger = ergebnis.ergebnis_summe

                    h = h + 0.5
                    if h > 28:
                        p.showPage()
                        h = 1
                        p.setFont('DejaVuSans', 8)

                current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
                p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

            p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Ergebnislisten_Ligaturnen_Einzel.pdf")


@login_required
@permission_required('ligaturnen.add_ligaturnenergebnisse')
def report_urkunde_mannschaft(request):
    ligen = Ligen.objects.all()
    vereine = Vereine.objects.all()
    ligaTag = LigaTag.objects.get(id=1)

    gender = ['w', 'm']

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Holen der Seitenabmessung
    breite, hoehe = A4

    hoehe_start = hoehe - 50
    for gen in gender:
        if gen == "w":
            gen_long = "weiblich"
        else:
            gen_long = "männlich"

        for liga in ligen:
            ergebnisse = LigaturnenErgebnisseZwischenLigaGesamt.objects.filter(liga=liga, gender=gen).order_by(
                '-ergebnis_summe')

            if ergebnisse:
                h = 1
                hilfsrang = 0
                rang = 1
                ergebnis_summe_vorheriger = 0
                for ergebnis in ergebnisse:
                    p.setFont('DejaVuSans', 22)
                    p.drawCentredString(breite / 2, hoehe_start - (18 * cm), str(ergebnis.liga) + "-Liga")
                    p.setFont('DejaVuSans', 12)
                    p.drawCentredString(breite / 2, hoehe_start - (18.6 * cm), gen_long)

                    p.setFont('DejaVuSans', 18)
                    p.drawCentredString(breite / 2, hoehe_start - (20 * cm), "Mit " + str(ergebnis.ergebnis_summe) +
                                        " Punkten belegte")

                    p.setFont('DejaVuSans', 18)
                    p.drawCentredString(breite / 2, hoehe_start - (21 * cm),
                                        "die " + str(ergebnis.mannschaft) + ". Mannschaft")

                    p.setFont('DejaVuSans', 18)
                    p.drawCentredString(breite / 2, hoehe_start - (22 * cm), str(ergebnis.verein.verein_name_kurz))

                    if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                        hilfsrang = hilfsrang + 1
                        rang = rang - 1
                        p.drawCentredString(breite / 2, hoehe_start - (23 * cm), str(rang) + ". Platz")
                        rang = rang + 1
                    else:
                        if hilfsrang > 0:
                            rang = rang + hilfsrang
                        p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "den " + str(rang) + ". Platz.")
                        rang = rang + 1
                        hilfsrang = 0

                    ergebnis_summe_vorheriger = ergebnis.ergebnis_summe
                    h = h + 0.5
                    #rang = rang + 1

                    p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Urkunde_Mannschaft.pdf")


@login_required
@permission_required('ligaturnen.add_ligaturnenergebnisse')
def report_urkunde_einzel(request):
    ligen = Ligen.objects.all()
    ligaTag = LigaTag.objects.get(id=1)

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Holen der Seitenabmessung
    breite, hoehe = A4
    hoehe_start = hoehe + 50
    #print(hoehe_start)

    gender = ['w', 'm']

    for gen in gender:
        if gen == "w":
            gen_long = "weiblich"
        else:
            gen_long = "männlich"

        for liga in ligen:

            ergebnisse = LigaturnenErgebnisseZwischenEinzel.objects.filter(
                teilnehmer_gender=gen, teilnehmer_liga=liga
            ).order_by('-ergebnis_summe')

            if ergebnisse:
                h = 1
                #hilfsrang = 0
                #rang = 1
                ergebnis_summe_vorheriger = 0
                h = h + 0.5
                for ergebnis in ergebnisse:
                    p.setFont('DejaVuSans-Bold', 18)
                    p.drawCentredString(breite / 2, hoehe_start - (18 * cm),
                                        str(ergebnis.teilnehmer_vorname) + " " +
                                        str(ergebnis.teilnehmer_name))

                    p.setFont('DejaVuSans', 18)

                    p.drawCentredString(breite / 2, hoehe_start - (19 * cm),
                                        " *" + str(
                                            datetime.strptime(str(ergebnis.teilnehmer_geburtsjahr), "%Y-%m-%d").year))
                    p.drawCentredString(breite / 2, hoehe_start - (20 * cm),
                                        str(ergebnis.teilnehmer_verein.verein_name_kurz))

                    p.drawCentredString(breite / 2, hoehe_start - (21 * cm),
                                        "erreichte eine Gesamtpunktzahl von:")

                    p.setFont('DejaVuSans-Bold', 18)
                    p.drawCentredString(breite / 2, hoehe_start - (22 * cm), str(ergebnis.ergebnis_summe))

                    p.setFont('DejaVuSans', 18)
                    p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "Punkten")

                    p.setFont('DejaVuSans', 12)
                    p.drawCentredString(breite / 2, hoehe_start - (24 * cm), "Einzelergebnisse:")

                    p.setFont('DejaVuSans', 10)
                    p.drawString(5.0 * cm, hoehe_start - (25 * cm), 'Schwebebalken:')
                    p.drawString(5.0 * cm, hoehe_start - (25.5 * cm), 'Reck/Stufenbarren:')
                    p.drawString(5.0 * cm, hoehe_start - (26 * cm), 'Minitrampolin:')

                    p.drawString(9.0 * cm, hoehe_start - (25 * cm), str(ergebnis.ergebnis_balken_s))
                    p.drawString(9.0 * cm, hoehe_start - (25.5 * cm), str(ergebnis.ergebnis_reck_s))
                    p.drawString(9.0 * cm, hoehe_start - (26 * cm), str(ergebnis.ergebnis_mini_s))

                    p.drawString(13.0 * cm, hoehe_start - (25 * cm), 'Boden:')
                    p.drawString(13.0 * cm, hoehe_start - (25.5 * cm), 'Barren:')
                    p.drawString(13.0 * cm, hoehe_start - (26 * cm), 'Sprung:')

                    p.drawString(15.0 * cm, hoehe_start - (25 * cm), str(ergebnis.ergebnis_boden_s))
                    p.drawString(15.0 * cm, hoehe_start - (25.5 * cm), str(ergebnis.ergebnis_barren_s))
                    p.drawString(15.0 * cm, hoehe_start - (26 * cm), str(ergebnis.ergebnis_sprung_s))

                    p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Urkunden_Einzel.pdf")


##########################################################################
# Area Auswertung Vereine
##########################################################################
@login_required
@permission_required('ligaturnen.add_ligaturnenergebnisse')
def report_auswertung_vereine(request):
    vereine = Vereine.objects.all()
    ligaTag = LigaTag.objects.get(id=1)

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=A4)

    # Holen der Seitenabmessung
    breite, hoehe = A4

    for verein in vereine:

        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Ligaturnen " + str(ligaTag.ligajahr))
        h = h + 0.8

        p.setFont('DejaVuSans-Bold', 14)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Verein: " + str(verein))
        h = h + 1

        ergebnisse = (LigaturnenErgebnisse.objects.filter(ergebnis_teilnehmer__teilnehmer_verein=verein, ergebnis_ligatag = 1)
                      .order_by("-ergebnis_teilnehmer__teilnehmer_gender", "ergebnis_teilnehmer__teilnehmer_geburtsjahr", "ergebnis_teilnehmer__teilnehmer_name"))

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, '1. Wettkampftag')

        h = h + 0.5
        p.setFont('DejaVuSans-Bold', 8)
        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Jahrg.')
        p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'w/m')
        p.drawString(2.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Liga')
        p.drawString(3.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
        p.drawString(9 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
        p.drawString(10.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
        p.drawString(12.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
        p.drawString(13.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
        p.drawString(15.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
        p.drawString(17.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
        p.drawString(18.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')
        # p.drawString(19.3 * cm, hoehe - (h * cm) + 0.2 * cm, 'Medaillie')

        h = h + 0.3
        p.setFont('DejaVuSans', 8)
        for ergebnis in ergebnisse:
            p.drawString(0.5 * cm, hoehe - (h * cm),
                         str(datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr), "%Y-%m-%d").year))
            p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_gender))
            p.drawString(2.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_liga))
            p.drawString(3.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_name) + " " +
                         str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname))
            p.drawString(9 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
            p.drawString(10.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
            p.drawString(12.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
            p.drawString(13.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
            p.drawString(15.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
            p.drawString(17.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
            p.drawString(18.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))

            h = h + 0.5
            if h > 28:
                p.showPage()
                h = 1
                p.setFont('DejaVuSans', 8)

        h = h + 0.5
        ergebnisse = (LigaturnenErgebnisse.objects.filter(ergebnis_teilnehmer__teilnehmer_verein=verein, ergebnis_ligatag = 2)
                      .order_by("-ergebnis_teilnehmer__teilnehmer_gender", "ergebnis_teilnehmer__teilnehmer_geburtsjahr", "ergebnis_teilnehmer__teilnehmer_name"))

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, '2. Wettkampftag')

        h = h + 0.5
        p.setFont('DejaVuSans-Bold', 8)
        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Jahrg.')
        p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'w/m')
        p.drawString(2.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Liga')
        p.drawString(3.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
        p.drawString(9 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
        p.drawString(10.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
        p.drawString(12.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
        p.drawString(13.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
        p.drawString(15.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
        p.drawString(17.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
        p.drawString(18.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')
        # p.drawString(19.3 * cm, hoehe - (h * cm) + 0.2 * cm, 'Medaillie')

        h = h + 0.3
        p.setFont('DejaVuSans', 8)
        for ergebnis in ergebnisse:
            p.drawString(0.5 * cm, hoehe - (h * cm),
                         str(datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr), "%Y-%m-%d").year))
            p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_gender))
            p.drawString(2.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_liga))
            p.drawString(3.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_name) + " " +
                         str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname))
            p.drawString(9 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
            p.drawString(10.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
            p.drawString(12.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
            p.drawString(13.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
            p.drawString(15.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
            p.drawString(17.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
            p.drawString(18.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))

            h = h + 0.5
            if h > 28:
                p.showPage()
                h = 1
                p.setFont('DejaVuSans', 8)

        h = h + 0.5
        ergebnisse = (LigaturnenErgebnisseZwischenEinzel.objects.filter(teilnehmer_verein=verein)
                      .order_by("-teilnehmer_gender", "teilnehmer_geburtsjahr", "teilnehmer_name"))

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamtergebnis')

        h = h + 0.5
        p.setFont('DejaVuSans-Bold', 8)
        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Jahrg.')
        p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'w/m')
        p.drawString(2.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Liga')
        p.drawString(3.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
        p.drawString(9 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
        p.drawString(10.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
        p.drawString(12.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
        p.drawString(13.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
        p.drawString(15.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
        p.drawString(17.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
        p.drawString(18.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')
        # p.drawString(19.3 * cm, hoehe - (h * cm) + 0.2 * cm, 'Medaillie')

        h = h + 0.3
        p.setFont('DejaVuSans', 8)
        for ergebnis in ergebnisse:
            p.drawString(0.5 * cm, hoehe - (h * cm),
                         str(datetime.strptime(str(ergebnis.teilnehmer_geburtsjahr), "%Y-%m-%d").year))
            p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_gender))
            p.drawString(2.5 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_liga))
            p.drawString(3.5 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_name) + " " +
                         str(ergebnis.teilnehmer_vorname))
            p.drawString(9 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
            p.drawString(10.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
            p.drawString(12.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
            p.drawString(13.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
            p.drawString(15.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
            p.drawString(17.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
            p.drawString(18.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))

            h = h + 0.5


        current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
        p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

        p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Ergebnislisten_Vereine.pdf")


##########################################################################
# Area Verein Upload
##########################################################################
@login_required
@permission_required('ligaturnen.add_vereine')
def vereine_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            vereine_handle_uploaded_file(request.FILES['file'])
            return redirect('/ligaturnen/vereine_list/')
    else:
        form = UploadFileForm()
    return render(request, 'ligaturnen/vereine_upload.html', {'form': form})


def vereine_handle_uploaded_file(file):
    # Lese die Daten aus der Excel-Datei
    df = pd.read_excel(file, na_filter=False)

    # Iteriere durch die Zeilen und speichere die Daten in der Datenbank
    for index, row in df.iterrows():
        vereine_neu = Vereine(verein_name=row['verein_name'],
                              verein_name_kurz=row['verein_name_kurz'],
                              verein_strasse=row['verein_strasse'],
                              verein_plz=row['verein_plz'],
                              verein_ort=row['verein_ort'],
                              verein_telefon=row['verein_telefon'],
                              verein_email=row['verein_email']
                              )
        try:
            vereine_neu.save()
        except:
            pass


##########################################################################
# Area Löschen Tabellen Ligaturnen Ergebnisse und Teilnehmer
##########################################################################

@login_required
@permission_required('ligaturnen.add_vereine')
def ligaturnen_tables_delete(request):
    if request.method == 'POST':
        count_ergebnisse = LigaturnenErgebnisse.objects.all().delete()
        count_ergebnisse_zwischen_einzel = LigaturnenErgebnisseZwischenLiga.objects.all().delete()
        count_ergebnisse_zwischen_liga = LigaturnenErgebnisseZwischenEinzel.objects.all().delete()
        count_teilnehmer = Teilnehmer.objects.all().delete()

        #Autoincrement Feld zurücksetzen
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sqlite_sequence SET seq = "
                               "(SELECT MAX(id) FROM 'ligaturnen_ligaturnenergebnisse') "
                               "WHERE name='ligaturnen_ligaturnenergebnisse'")

                cursor.execute("UPDATE sqlite_sequence SET seq = "
                               "(SELECT MAX(id) FROM 'ligaturnen_ligaturnenergebnissezwischenliga') "
                               "WHERE name='ligaturnen_ligaturnenergebnissezwischenliga'")

                cursor.execute("UPDATE sqlite_sequence SET seq = "
                               "(SELECT MAX(id) FROM 'ligaturnen_ligaturnenergebnissezwischeneinzel') "
                               "WHERE name='ligaturnen_ligaturnenergebnissezwischeneinzel'")

                cursor.execute("UPDATE sqlite_sequence SET seq = "
                               "(SELECT MAX(id) FROM 'ligaturnen_teilnehmer') "
                               "WHERE name='ligaturnen_teilnehmer'")

        elif connection.vendor == 'mysql':
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE ligaturnen_ligaturnenergebnisse AUTO_INCREMENT = 1;")

                cursor.execute(
                    "ALTER TABLE ligaturnen_ligaturnenergebnissezwischenliga AUTO_INCREMENT = 1;")

                cursor.execute(
                    "ALTER TABLE ligaturnen_ligaturnenergebnissezwischeneinzel AUTO_INCREMENT = 1;")

                cursor.execute(
                    "ALTER TABLE ligaturnen_teilnehmer AUTO_INCREMENT = 1;")

        return redirect('/ligaturnen/teilnehmer_list/')
    else:
        pass

    form = TablesDeleteForm()
    return render(request, 'ligaturnen/tables_delete.html', {'form': form})

@login_required
@permission_required('ligaturnen.add_teilnehmer')
def check_rules(request):
    mannschaften = [1, 2, 3]
    #ligen = ['A', 'B', 'C', 'D', 'E', 'F']
    ligen = Ligen.objects.all().order_by('liga')
    vereine = Vereine.objects.all()
    ligatag = LigaTag.objects.get()
    mannschaft_error = []
    for verein in vereine:
        for liga in ligen:
            for mannschaft in mannschaften:
                teilnehmer_mannschaft = Teilnehmer.objects.filter(teilnehmer_mannschaft=mannschaft,
                                                                  teilnehmer_verein=verein,
                                                                  teilnehmer_ak=False,
                                                                  teilnehmer_liga_tag = ligatag,
                                                                  teilnehmer_liga = liga
                                                                  )

                if teilnehmer_mannschaft.count() > 6:
                    #print(f"Ligatag: {ligatag}; Liga: {liga}; Verein: {verein}; Mannschaft: {mannschaft}, {str(teilnehmer_mannschaft)}  ")
                    mannschaft_error.append(f"{verein}; {mannschaft}. Mannschaft hat zu viele Teilnehmer ({teilnehmer_mannschaft.count()} Teilnehmer) beim {ligatag}. Ligatag")

                for teil_mannschaft in teilnehmer_mannschaft:
                    #jahrgang = datetime.strptime(str(teil_mannschaft.teilnehmer_geburtsjahr), "%Y-%m-%d").year

                    if teil_mannschaft.teilnehmer_geburtsjahr < liga.liga_ab:
                        print(f"{teil_mannschaft.teilnehmer_geburtsjahr} {liga.liga_ab} {verein} {liga} {mannschaft} {teil_mannschaft.teilnehmer_name} Falscher Jahrgang")

    return render(request, 'ligaturnen/check_rules.html', {'mannschaft_error': mannschaft_error})
