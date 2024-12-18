import io
import os
from time import strftime
import logging

import pandas as pd
from datetime import datetime
from dateutil import parser

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.http import FileResponse
from django.db import connection

from reportlab.lib.enums import TA_CENTER

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, Spacer

from weasyprint import HTML, CSS

import ligaturnen.models
from turnverein.settings import BASE_DIR

from .models import Vereine, Teilnehmer, Geraete, Riegen, BezirksturnfestErgebnisse, Meisterschaften, Konfiguration
from .forms import UploadFileForm, ErgebnisTeilnehmerSuchen, VereinErfassenForm, TeilnehmerErfassenForm, \
    ErgebnisTeilnehmererfassenForm, TablesDeleteForm

logger = logging.getLogger(__name__)


# assert False

##########################################################################
# Area allgemeine Seiten
##########################################################################
@login_required
def index(request):
    conf_liegaturnen = ligaturnen.models.Konfiguration.objects.get(id=1)
    conf_bezirksturnfest = Konfiguration.objects.get(id=1)
    return render(request, 'turnfest/index.html',
                  {'conf_bezirksturnfest': conf_bezirksturnfest, 'conf_ligaturnen': conf_liegaturnen})


@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def bezirksturnfest(request):
    request.session['geraet'] = ""
    request.session['teilnehmer'] = ""

    return render(request, 'turnfest/bezirksturnfest.html')


@login_required
@permission_required('ligaturnen.view_ligaturnenergebnisse')
def ligawettkampf(request):
    return render(request, 'turnfest/ligawettkampf.html')


def impressum(request):
    return render(request, 'turnfest/impressum.html')


def datenschutz(request):
    return render(request, 'turnfest/datenschutz.html')


##########################################################################
# Area Verein create and change
##########################################################################
class VereineCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "turnfest.add_vereine"
    model = Vereine
    template_name = "turnfest/vereine_create.html"
    form_class = VereinErfassenForm
    success_url = reverse_lazy("turnfest:vereine_list")


class VereineListView(PermissionRequiredMixin, ListView):
    permission_required = "turnfest.view_vereine"
    model = Vereine


class VereineDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "turnfest.view_vereine"
    model = Vereine


class VereineUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "turnfest.change_vereine"
    model = Vereine
    template_name = "turnfest/vereine_edit.html"
    fields = '__all__'
    success_url = "/turnfest/vereine_list/"


class VereineDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "turnfest.delete_vereine"
    model = Vereine
    template_name = "turnfest/vereine_delete.html"
    success_url = reverse_lazy("turnfest:vereine_list")


@login_required
@permission_required('turnfest.view_vereine')
def report_vereine(request):
    vereine = Vereine.objects.filter(verein_aktiv=True)

    html_file = 'pdf_templates/report_vereine.html'
    css_file = '/css/report_vereine.css'

    filename = "vereine.pdf"

    html_string = render_to_string(html_file, {'vereine': vereine})

    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    pdf = html.write_pdf(stylesheets=[CSS(settings.STATIC_ROOT + css_file)])
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response


@login_required
@permission_required('turnfest.view_vereine')
def vereine_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            vereine_handle_uploaded_file(request.FILES['file'])
            return redirect('/turnfest/vereine_list/')
    else:
        form = UploadFileForm()
    return render(request, 'turnfest/vereine_upload.html', {'form': form})


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
# Area Teilnehmer create and change
##########################################################################
class TeilnehmerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "turnfest.add_teilnehmer"
    model = Teilnehmer
    template_name = "turnfest/teilnehmer_create.html"
    form_class = TeilnehmerErfassenForm
    # fields = '__all__'
    success_url = reverse_lazy("turnfest:teilnehmer_list")


class TeilnehmerList(PermissionRequiredMixin, ListView):
    permission_required = "turnfest.view_teilnehmer"
    model = Teilnehmer
    ordering = ['-teilnehmer_geburtsjahr', 'teilnehmer_verein', 'teilnehmer_name', 'teilnehmer_vorname']


class TeilnehmerDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "turnfest.view_teilnehmer"
    model = Teilnehmer


class TeilnehmerUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "turnfest.change_teilnehmer"
    model = Teilnehmer
    template_name = "turnfest/teilnehmer_edit.html"
    # fields = '__all__'
    form_class = TeilnehmerErfassenForm
    success_url = reverse_lazy("turnfest:teilnehmer_list")


class TeilnehmerDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "turnfest.delete_teilnehmer"
    model = Teilnehmer
    template_name = "turnfest/teilnehmer_delete.html"
    success_url = reverse_lazy("turnfest:teilnehmer_list")


@login_required
@permission_required('turnfest.view_teilnehmer')
def teilnehmer_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            countdict = handle_uploaded_file(request.FILES['file'])
            request.session['count_positiv_turnfest'] = str(countdict["count_positiv"])
            request.session['count_negativ_turnfest'] = str(countdict["count_negativ"])
            logger.info(f"User {request.user.id} hat eine neue Teilnehmerliste hochgeladen")
            if countdict["name_fault"]:
                request.session['name_fault'] = str(countdict["name_fault"])
                form = UploadFileForm()
                return render(request, 'turnfest/teilnehmer_upload.html', {'form': form})
            return redirect('/turnfest/teilnehmer_list/')
    else:
        request.session['name_fault'] = ""
        form = UploadFileForm()
    return render(request, 'turnfest/teilnehmer_upload.html', {'form': form})


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

        if isinstance(row['Sprung'], int):
            Sprung = row['Sprung']
        else:
            Sprung = 0

        if isinstance(row['Minitrampolin'], int):
            Minitrampolin = row['Minitrampolin']
        else:
            Minitrampolin = 0

        if isinstance(row['Reck_Stufenbarren'], int):
            Reck_Stufenbarren = row['Reck_Stufenbarren']
        else:
            Reck_Stufenbarren = 0

        if isinstance(row['Schwebebalken'], int):
            Schwebebalken = row['Schwebebalken']
        else:
            Schwebebalken = 0

        if isinstance(row['Barren'], int):
            Barren = row['Barren']
        else:
            Barren = 0

        if isinstance(row['Boden'], int):
            Boden = row['Boden']
        else:
            Boden = 0

        if Sprung > 0:
            counter_geraet = counter_geraet + 1
        if Minitrampolin > 0:
            counter_geraet = counter_geraet + 1
        if Reck_Stufenbarren > 0:
            counter_geraet = counter_geraet + 1
        if Schwebebalken > 0:
            counter_geraet = counter_geraet + 1
        if Barren > 0:
            counter_geraet = counter_geraet + 1
        if Boden > 0:
            counter_geraet = counter_geraet + 1

        Geburtsjahr = str(row['Geburtsjahr'])



        if len(Geburtsjahr) == 4:
            Geburtsjahr = Geburtsjahr + "-01-01"
        else:
            datum_obj = parser.parse(Geburtsjahr)
            Geburtsjahr = datum_obj.strftime("%Y-%m-%d")

        if counter_geraet <= 4:
            Teilnehmer_neu = Teilnehmer(teilnehmer_name=row['Nachname'],
                                        teilnehmer_vorname=row['Vorname'],
                                        teilnehmer_gender=row['Geschlecht'],
                                        teilnehmer_geburtsjahr=Geburtsjahr,
                                        teilnehmer_verein_id=row['Verein'],
                                        teilnehmer_anwesend="True",
                                        teilnehmer_sprung=Sprung,
                                        teilnehmer_mini=Minitrampolin,
                                        teilnehmer_reck_stufenbarren=Reck_Stufenbarren,
                                        teilnehmer_balken=Schwebebalken,
                                        teilnehmer_barren=Barren,
                                        teilnehmer_boden=Boden,
                                        )
            try:
                Teilnehmer_neu.save()
                count_positiv = count_positiv + 1
            except Exception as inst:
                logger.info(inst.args)
                count_negativ = count_negativ + 1
        else:
            name_fault = row['Nachname'] + " " + row['Vorname']
            countdict = {"count_positiv": count_positiv, "count_negativ": count_negativ, "name_fault": name_fault}
            return countdict

    countdict = {"count_positiv": count_positiv, "count_negativ": count_negativ, "name_fault": name_fault}
    return countdict


##########################################################################
# Area Wettkampflisten erzeugen
##########################################################################
@login_required
@permission_required('turnfest.view_teilnehmer')
def report_geraetelisten(request):
    riegen = Riegen.objects.all()
    geraete = Geraete.objects.all()
    konfiguration = Konfiguration.objects.get(id=1)

    # Definieren Sie die gewünschte Schriftart und laden Sie sie
    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    response = HttpResponse(content_type='application/pdf')
    #response['Content-Disposition'] = 'inline; filename="Wettkampfliste.pdf"'
    response['Content-Disposition'] = 'attachment; filename="Wettkampfliste.pdf"'

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

    styles.add(ParagraphStyle(name='CenterAlign12',
                              fontName='DejaVuSans-Bold',
                              fontSize=12,
                              alignment=TA_CENTER))

    normal_style = styles['Normal']
    heading_style = styles['Heading1']
    heading_style.alignment = TA_CENTER

    # Create a list to store the content for the PDF
    content = []
    # teilnehmer_alle = []
    for riege in riegen:
        for geraet in geraete:

            if geraet.geraet_db_name == "teilnehmer_sprung":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_sprung__gt=0,
                    teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                   riege.riege_bis]).values_list('id',
                                                                                 'teilnehmer_name',
                                                                                 'teilnehmer_vorname',
                                                                                 'teilnehmer_verein__verein_name_kurz',
                                                                                 'teilnehmer_geburtsjahr',
                                                                                 'teilnehmer_sprung'
                                                                                 ).order_by('teilnehmer_sprung')
            elif geraet.geraet_db_name == "teilnehmer_mini":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_mini__gt=0,
                    teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                   riege.riege_bis]).values_list('id',
                                                                                 'teilnehmer_name',
                                                                                 'teilnehmer_vorname',
                                                                                 'teilnehmer_verein__verein_name_kurz',
                                                                                 'teilnehmer_geburtsjahr',
                                                                                 'teilnehmer_mini'
                                                                                 ).order_by('teilnehmer_mini')
            elif geraet.geraet_db_name == "teilnehmer_reck_stufenbarren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_reck_stufenbarren__gt=0,
                    teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                   riege.riege_bis]).values_list('id',
                                                                                 'teilnehmer_name',
                                                                                 'teilnehmer_vorname',
                                                                                 'teilnehmer_verein__verein_name_kurz',
                                                                                 'teilnehmer_geburtsjahr',
                                                                                 'teilnehmer_reck_stufenbarren'
                                                                                 ).order_by(
                    'teilnehmer_reck_stufenbarren')
            elif geraet.geraet_db_name == "teilnehmer_balken":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_balken__gt=0,
                    teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                   riege.riege_bis]).values_list('id',
                                                                                 'teilnehmer_name',
                                                                                 'teilnehmer_vorname',
                                                                                 'teilnehmer_verein__verein_name_kurz',
                                                                                 'teilnehmer_geburtsjahr',
                                                                                 'teilnehmer_balken'
                                                                                 ).order_by('teilnehmer_balken')
            elif geraet.geraet_db_name == "teilnehmer_barren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_barren__gt=0,
                    teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                   riege.riege_bis]).values_list('id',
                                                                                 'teilnehmer_name',
                                                                                 'teilnehmer_vorname',
                                                                                 'teilnehmer_verein__verein_name_kurz',
                                                                                 'teilnehmer_geburtsjahr',
                                                                                 'teilnehmer_barren'
                                                                                 ).order_by('teilnehmer_barren')
            elif geraet.geraet_db_name == "teilnehmer_boden":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_boden__gt=0,
                    teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                   riege.riege_bis]).values_list('id',
                                                                                 'teilnehmer_name',
                                                                                 'teilnehmer_vorname',
                                                                                 'teilnehmer_verein__verein_name_kurz',
                                                                                 'teilnehmer_geburtsjahr',
                                                                                 'teilnehmer_boden'
                                                                                 ).order_by('teilnehmer_boden')

            if teilnehmer_alle:
                # Add a heading to the PDF
                content.append(Paragraph('Bezirksturnfest ' + str(konfiguration.jahr), styles['CenterAlign20']))
                content.append(Spacer(1, 4))

                # Add a line to the PDF
                content.append(Paragraph(
                    "____________________________________________________________________________________________________",
                    normal_style))
                content.append(Spacer(1, 4))

                content.append(Paragraph(riege.riege + " " + geraet.geraet_name, styles['CenterAlign14']))
                content.append(Spacer(1, 12))

                headers = ['Start-Nr.', 'Nachname', 'Vorname', 'Verein', 'Jahrgang', 'Meldung', 'A-Note*', 'B-Note',
                           'Summe']
                table_data = [headers] + [list(row) + [''] * (len(headers) - len(row)) for row in teilnehmer_alle]
                if table_data:
                    t = Table(table_data, colWidths=[40, 100, 100, 70, 60, 40, 40, 40, 40])
                    content.append(t)
                    content.append(Spacer(1, 4))
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                        ('FONT', (0, 0), (-1, -1), 'DejaVuSans'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                        ('ALIGN', (5, 0), (5, -1), 'CENTER')
                    ]))

                content.append(Paragraph(
                    "*: A-Note nur eintragen, wenn es eine Änderung zur Meldung gegeben hat!", normal_style))

                content.append(PageBreak())

    # Add more content as needed...
    # Build the PDF
    pdf.build(content)

    return response


@login_required
@permission_required('turnfest.view_teilnehmer')
def report_meldungen_vereine(request):
    konfiguration = Konfiguration.objects.get(id=1)

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

    vereine = Vereine.objects.filter(verein_aktiv=True)
    riegen = Riegen.objects.all()

    for verein in vereine:

        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), konfiguration.bezirksturnfest + " " + str(konfiguration.jahr))
        h = h + 1
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Meldungen " + str(verein))
        h = h + 1

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)

        p.setFillGray(0.0)
        p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
        p.drawString(5.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Jahrgang')
        p.drawString(8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
        p.drawString(9.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
        p.drawString(11.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
        p.drawString(12.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
        p.drawString(14.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
        p.drawString(16.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
        anzahl_teilnehmer = 0
        for riege in riegen:
            ergebnisse = (Teilnehmer.objects.filter(teilnehmer_verein=verein,
                                                    teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                   riege.riege_bis]).
                          order_by('teilnehmer_geburtsjahr'))
            p.setFont('DejaVuSans-Bold', 8)
            h = h + 1
            p.drawString(1.5 * cm, hoehe -(h *cm), str(riege))
            p.setFont('DejaVuSans', 8)
            for ergebnis in ergebnisse:
                if h > 24:
                    p.showPage()
                    h = 1
                    p.setFont('DejaVuSans', 8)

                    p.setFillGray(0.75)
                    p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)

                    p.setFillGray(0.0)
                    p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
                    p.drawString(5.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Jahrgang')
                    p.drawString(8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
                    p.drawString(9.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
                    p.drawString(11.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
                    p.drawString(12.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
                    p.drawString(14.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
                    p.drawString(16.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
                    p.setFont('DejaVuSans', 8)


                h = h + 0.4
                jahr = datetime.strptime(str(ergebnis.teilnehmer_geburtsjahr), "%Y-%m-%d").year
                p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_name) + " " +
                             str(ergebnis.teilnehmer_vorname))
                p.drawString(5.5 * cm, hoehe - (h * cm), str(jahr))
                p.drawString(8 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_sprung))
                p.drawString(9.6 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_mini))
                p.drawString(11.2 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_reck_stufenbarren))
                p.drawString(12.8 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_balken))
                p.drawString(14.4 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_barren))
                p.drawString(16.0 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_boden))
                anzahl_teilnehmer = anzahl_teilnehmer + 1

        p.setFont('DejaVuSans-Bold', 8)
        h = h + 1
        p.drawString(1.5 * cm, hoehe - (h * cm), "Anzahl gemeldete Teilnehmer: " + str(anzahl_teilnehmer))
        p.setFont('DejaVuSans', 8)
        p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Meldungen_Vereine.pdf")

##########################################################################
# Area Ergebnisse erfassen
##########################################################################
@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def ergebnis_erfassen_suche(request):
    if request.method == "POST":
        startnummer = request.POST['startnummer']
        geraete_id = request.POST['geraet']
        request.session['startnummer'] = str(startnummer)
        request.session['geraet'] = str(geraete_id)

        try:
            teilnehmer = Teilnehmer.objects.get(id=startnummer)
            try:
                ergebnis = BezirksturnfestErgebnisse.objects.get(ergebnis_teilnehmer=startnummer)
                return redirect("/turnfest/edit/ergebnis/" + str(ergebnis.id) + '/')
            except:
                return redirect("/turnfest/add/ergebnis" + "/?start=" + startnummer)
        except:
            form = ErgebnisTeilnehmerSuchen()
            form.startnummerfalse = True
            return render(request, 'turnfest/ergebnis_erfassen_suche.html', {'form': form})

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
            try:
                ergebnis = BezirksturnfestErgebnisse.objects.get(id=teilnehmer_id)
            except:
                ergebnis = ""
        else:
            ergebnis = ""
        form = ErgebnisTeilnehmerSuchen()
        form.geraet_option = geraet_option

    return render(request, 'turnfest/ergebnis_erfassen_suche.html', {'form': form, 'ergebnis': ergebnis})


@login_required
@permission_required('turnfest.change_bezirksturnfestergebnisse')
def add_ergebnis(request):
    if request.method == "POST":
        form = ErgebnisTeilnehmererfassenForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            request.session['teilnehmer'] = str(item.id)
            return redirect('/turnfest/ergebnis_erfassen_suche/')
        for field in form:
            print("Field Error:", field.name, field.errors)
    else:
        teilnehmer = Teilnehmer.objects.get(id=request.session['startnummer'])

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
        form.add = True  # Damit im Formular die hidden Felder eingeblendet werden
    return render(request, 'turnfest/ergebnis_erfassen.html', {'form': form})


@login_required
@permission_required('turnfest.change_bezirksturnfestergebnisse')
def edit_ergebnis(request, id=None):
    item = get_object_or_404(BezirksturnfestErgebnisse, id=id)

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

    if form.is_valid():
        form.save()
        request.session['teilnehmer'] = id
        return redirect('/turnfest/ergebnis_erfassen_suche/')

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
    return render(request, 'turnfest/ergebnis_erfassen.html', {'form': form})


class ErgebnisseList(PermissionRequiredMixin, ListView):
    permission_required = "turnfest.add_bezirksturnfestergebnisse"
    model = BezirksturnfestErgebnisse
    template_name = "turnfest/ergebnisse_list.html"
    ordering = ['ergebnis_teilnehmer__teilnehmer_verein',
                'ergebnis_teilnehmer__teilnehmer_name',
                'ergebnis_teilnehmer__teilnehmer_vorname']

class ErgebnisseCheck(PermissionRequiredMixin, ListView):
    permission_required = "turnfest.add_bezirksturnfestergebnisse"
    model = BezirksturnfestErgebnisse
    template_name = "turnfest/ergebnisse_check.html"
    ordering = ['ergebnis_teilnehmer__id']


##########################################################################
# Area Auswertung Bezirksturnfest erfassen
##########################################################################
@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def report_auswertung(request):
    meisterschaften = Meisterschaften.objects.order_by('-meisterschaft_gender')
    konfiguration = Konfiguration.objects.get(id=1)

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

    count_bronze = BezirksturnfestErgebnisse.objects.filter(ergebnis_summe__range=(16, 48)).count()
    count_silber = BezirksturnfestErgebnisse.objects.filter(ergebnis_summe__range=(48, 64)).count()
    count_gold = BezirksturnfestErgebnisse.objects.filter(ergebnis_summe__range=(64, 1000)).count()
    count_keine = BezirksturnfestErgebnisse.objects.filter(ergebnis_summe__range=(0, 16)).count()
    print(f"Anzahl silber: {count_silber}")
    print(f"Anzahl keine: {count_keine}")

    h = 1
    p.setFont('DejaVuSans-Bold', 18)
    p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Bezirksturnfest " + str(konfiguration.jahr))
    h = h + 0.8
    p.setFont('DejaVuSans-Bold', 14)
    p.drawCentredString(breite / 2, hoehe - (h * cm), "Gesamtauswertung ")
    h = h + 1

    #p.setFont('DejaVuSans', 8)

    p.setFillGray(0.75)
    p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
    h = h + 2
    p.setFillGray(0.0)
    p.drawString(7 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gold-Medaillen:')
    p.drawRightString(14.5 * cm, hoehe - (h * cm) + 0.2 * cm, str(count_gold))
    h = h + 1
    p.drawString(7 * cm, hoehe - (h * cm) + 0.2 * cm, 'Silber-Medaillen:')
    p.drawRightString(14.5 * cm, hoehe - (h * cm) + 0.2 * cm, str(count_silber))
    h = h + 1
    p.drawString(7 * cm, hoehe - (h * cm) + 0.2 * cm, 'Bronze-Medaillen:')
    p.drawRightString(14.5 * cm, hoehe - (h * cm) + 0.2 * cm, str(count_bronze))
    h = h + 1
    p.drawString(7 * cm, hoehe - (h * cm) + 0.2 * cm, 'keine Medaille:')
    p.drawRightString(14.5 * cm, hoehe - (h * cm) + 0.2 * cm, str(count_keine))

    p.showPage()

    for meisterschaft in meisterschaften:

        ergebnisse = (BezirksturnfestErgebnisse.objects.filter(
            ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(meisterschaft.meisterschaft_ab),
            ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(meisterschaft.meisterschaft_bis),
            ergebnis_teilnehmer__teilnehmer_gender=meisterschaft.meisterschaft_gender).
                      order_by("ergebnis_teilnehmer__teilnehmer_geburtsjahr__year", '-ergebnis_summe'))

        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Bezirksturnfest " + str(konfiguration.jahr))
        h = h + 0.8
        p.setFont('DejaVuSans-Bold', 14)
        p.drawCentredString(breite / 2, hoehe - (h * cm), meisterschaft.meisterschaft + " " +
                            meisterschaft.get_meisterschaft_gender_display())
        h = h + 1

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)

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
        p.drawString(19.3 * cm, hoehe - (h * cm) + 0.2 * cm, 'Medaillie')

        # p.setFillColorRGB(0, 0, 0.77)

        # h = h + 1
        jahr_2 = ""
        rang = 1
        ergebnis_summe_vorheriger = 0
        for ergebnis in ergebnisse:
            jahr = datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr), "%Y-%m-%d").year
            if jahr != jahr_2:
                h = h + 1
                p.setFillColor(colors.aquamarine)
                p.rect(0.2 * cm, hoehe - (h * cm) + 0.4 * cm, 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
                p.setFillColor(colors.black)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.6 * cm, "Jahrgang: " + str(jahr))
                jahr_2 = jahr
                rang = 1
                ergebnis_summe_vorheriger = 0

            if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                rang = rang - 1
                p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                rang = rang + 1
            else:
                p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))

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

            if 16 <= ergebnis.ergebnis_summe < 48:
                medaille = 'Bronze'
            elif 48 <= ergebnis.ergebnis_summe < 64:
                medaille = 'Silber'
            elif ergebnis.ergebnis_summe >= 64:
                medaille = 'Gold'
            else:
                medaille = "-"

            p.drawString(19.3 * cm, hoehe - (h * cm), medaille)

            h = h + 0.5
            rang = rang + 1
            if h > 24:
                p.showPage()
                h = 1
        if ergebnisse:
            h = h + 1
            p.line(0.2 * cm, hoehe - (h * cm), 20.8 * cm, hoehe - (h * cm))

            h = h + 1
            p.setFillColorRGB(1, 0.6, 0.8)
            p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)

            p.setFillGray(0.0)
            p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm,
                         meisterschaft.meisterschaft + " " + meisterschaft.get_meisterschaft_gender_display())

            meister_innen = (BezirksturnfestErgebnisse.objects.filter(
                ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(meisterschaft.meisterschaft_ab),
                ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(meisterschaft.meisterschaft_bis),
                ergebnis_teilnehmer__teilnehmer_gender=meisterschaft.meisterschaft_gender).
                             order_by("-ergebnis_summe"))

            h = h + 0.5
            i = 0  # zähler
            ergebnis_zwischen = 0  # zwischenspeicherung des vorherigen ergebnisses
            for meister_in in meister_innen:
                if i > 0:
                    if ergebnis_zwischen == meister_in.ergebnis_summe:
                        p.drawString(1.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_teilnehmer))
                        p.drawString(5.0 * cm, hoehe - (h * cm),
                                     str(meister_in.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))
                        p.drawString(9.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_summe) + " " + "Punkte")
                else:
                    p.drawString(1.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_teilnehmer))
                    p.drawString(5.0 * cm, hoehe - (h * cm),
                                 str(meister_in.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))
                    p.drawString(9.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_summe) + " " + "Punkte")
                    # das Übertragen findet nur hier statt, weil es für die weiteren Plätze nicht relevant ist.
                    ergebnis_zwischen = meister_in.ergebnis_summe
                i = i + 1
                h = h + 0.4

        current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
        p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

        p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Ergebnislisten.pdf")


@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def report_urkunden(request):
    meisterschaften = Meisterschaften.objects.order_by('-meisterschaft_gender')
    konfiguration = Konfiguration.objects.get(id=1)

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

    for meisterschaft in meisterschaften:
        ergebnisse = BezirksturnfestErgebnisse.objects.filter(
            ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(meisterschaft.meisterschaft_ab),
            ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(meisterschaft.meisterschaft_bis),
            ergebnis_teilnehmer__teilnehmer_gender=meisterschaft.meisterschaft_gender
        ).order_by('ergebnis_teilnehmer__teilnehmer_geburtsjahr', '-ergebnis_summe')

        jahr_2 = ""
        rang = 1
        ergebnis_summe_vorheriger = 0
        for ergebnis in ergebnisse:
            h = 15
            jahr = datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr), "%Y-%m-%d").year
            if jahr != jahr_2:
                jahr_2 = jahr
                rang = 1
                ergebnis_summe_vorheriger = 0

            if 16 <= ergebnis.ergebnis_summe < 48:
                medaille = 'Bronze'
            elif 48 <= ergebnis.ergebnis_summe < 64:
                medaille = 'Silber'
            elif ergebnis.ergebnis_summe >= 64:
                medaille = 'Gold'
            else:
                medaille = "-"

            h = 18
            p.setFont('DejaVuSans-Bold', 18)
            #p.drawCentredString(breite / 2, hoehe - (h * cm), konfiguration.bezirksturnfest + " " +str(konfiguration.jahr))
            #h = h + 1
            #p.drawCentredString(breite / 2, hoehe - (h * cm), meisterschaft.meisterschaft)
            #h = h + 1
            #p.drawCentredString(breite / 2, hoehe - (h * cm), meisterschaft.meisterschaft_gender)
            #h = h + 1
            #p.drawCentredString(breite / 2, hoehe - (h * cm), medaille)
            #h = h + 1
            #p.drawCentredString(breite / 2, hoehe - (h * cm), "Jahrgang: " + str(jahr))
            #h = h + 1

            #if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
            #    rang = rang - 1
            #    p.drawCentredString(breite / 2, hoehe - (h * cm), "Rang: " + str(rang))
            #    rang = rang + 1
            #else:
            #    p.drawCentredString(breite / 2, hoehe - (h * cm), "Rang: " + str(rang))

            #h = h + 1
            #p.drawCentredString(breite / 2, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer))

            #ergebnis_summe_vorheriger = ergebnis.ergebnis_summe
            #rang = rang + 1
            p.setFont('DejaVuSans', 18)
            p.drawCentredString(breite / 2, hoehe_start - (17 * cm),
                                str(meisterschaft))

            p.setFont('DejaVuSans-Bold', 18)
            p.drawCentredString(breite / 2, hoehe_start - (18 * cm),
                                str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname) + " " +
                                str(ergebnis.ergebnis_teilnehmer.teilnehmer_name))

            p.setFont('DejaVuSans', 18)

            p.drawCentredString(breite / 2, hoehe_start - (19 * cm),
                                " *" + str(
                                    datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr),
                                                      "%Y-%m-%d").year))
            p.drawCentredString(breite / 2, hoehe_start - (20 * cm),
                                str(ergebnis.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))

            p.drawCentredString(breite / 2, hoehe_start - (21 * cm),
                                "erreichte eine Gesamtpunktzahl von:")

            p.setFont('DejaVuSans-Bold', 18)
            p.drawCentredString(breite / 2, hoehe_start - (22 * cm), str(ergebnis.ergebnis_summe) + " Punkten")

            p.setFont('DejaVuSans-Bold', 18)
            if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                rang = rang - 1
                p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "Rang: " + str(rang))
                rang = rang + 1
            else:
                p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "Rang: " + str(rang))

            #p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "und damit " + str(ergebnis.ergebnis_summe)) + " Punkten"
            #p.setFont('DejaVuSans', 18)
            #p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "Punkten")

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

            rang = rang + 1
            p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Urkunden_Bezirksturnfest.pdf")


@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def report_urkunden_jahrgang(request):
    meisterschaften = Meisterschaften.objects.order_by('-meisterschaft_gender')
    konfiguration = Konfiguration.objects.get(id=1)

    GENDER = ('w', 'm')

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


    for gen in GENDER:
        for jahrgang in range(2000, 2100):
            ergebnisse = BezirksturnfestErgebnisse.objects.filter(
                ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(jahrgang) + "-01-01",
                ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(jahrgang) + "-12-31",
                ergebnis_teilnehmer__teilnehmer_gender=gen
            ).order_by('-ergebnis_summe')
            if ergebnisse:
                #jahr_2 = ""
                rang = 1
                ergebnis_summe_vorheriger = 0
                for ergebnis in ergebnisse:
                    h = 15
                    #jahr = datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr), "%Y-%m-%d").year
                    #if jahr != jahr_2:
                    #    jahr_2 = jahr
                    #    rang = 1
                    #    ergebnis_summe_vorheriger = 0

                    if 16 <= ergebnis.ergebnis_summe < 48:
                        medaille = 'Bronze'
                    elif 48 <= ergebnis.ergebnis_summe < 64:
                        medaille = 'Silber'
                    elif ergebnis.ergebnis_summe >= 64:
                        medaille = 'Gold'
                    else:
                        medaille = "-"

                    h = 18
                    p.setFont('DejaVuSans-Bold', 18)
                    p.setFont('DejaVuSans', 18)

                    p.setFont('DejaVuSans-Bold', 18)
                    p.drawCentredString(breite / 2, hoehe_start - (18 * cm),
                                        str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname) + " " +
                                        str(ergebnis.ergebnis_teilnehmer.teilnehmer_name))

                    p.setFont('DejaVuSans', 18)

                    #p.drawCentredString(breite / 2, hoehe_start - (19 * cm),
                    #                    " *" + str(
                    #                        datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr),
                    #                                          "%Y-%m-%d").year))

                    p.drawCentredString(breite / 2, hoehe_start - (19 * cm),
                                        str(ergebnis.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))

                    p.drawCentredString(breite / 2, hoehe_start - (21 * cm),
                                        "erreicht eine Gesamtpunktzahl von " + str(ergebnis.ergebnis_summe) + " Punkten und ")

                    #p.setFont('DejaVuSans-Bold', 18)
                    #p.drawCentredString(breite / 2, hoehe_start - (22 * cm), "damit im Jahrgang " + jahrgang + " den " + rang + ". Rang")


                    #p.setFont('DejaVuSans-Bold', 18)
                    if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                        rang = rang - 1
                        p.drawCentredString(breite / 2, hoehe_start - (22 * cm), "damit im Jahrgang " + str(jahrgang) + " den " + str(rang) + ". Rang")
                        rang = rang + 1
                    else:
                        p.drawCentredString(breite / 2, hoehe_start - (22 * cm), "damit im Jahrgang " + str(jahrgang) + " den " + str(rang) + ". Rang")



                    #p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "und damit " + str(ergebnis.ergebnis_summe)) + " Punkten"
                    #p.setFont('DejaVuSans', 18)
                    #p.drawCentredString(breite / 2, hoehe_start - (23 * cm), "Punkten")

                    p.setFont('DejaVuSans', 12)
                    p.drawCentredString(breite / 2, hoehe_start - (23.5 * cm), "Einzelergebnisse:")

                    p.setFont('DejaVuSans', 10)
                    p.drawString(5.0 * cm, hoehe_start - (24 * cm), 'Schwebebalken:')
                    p.drawString(5.0 * cm, hoehe_start - (24.5 * cm), 'Reck/Stufenbarren:')
                    p.drawString(5.0 * cm, hoehe_start - (25 * cm), 'Minitrampolin:')

                    p.drawString(9.0 * cm, hoehe_start - (24 * cm), str(ergebnis.ergebnis_balken_s))
                    p.drawString(9.0 * cm, hoehe_start - (24.5 * cm), str(ergebnis.ergebnis_reck_s))
                    p.drawString(9.0 * cm, hoehe_start - (25 * cm), str(ergebnis.ergebnis_mini_s))

                    p.drawString(13.0 * cm, hoehe_start - (24 * cm), 'Boden:')
                    p.drawString(13.0 * cm, hoehe_start - (24.5 * cm), 'Barren:')
                    p.drawString(13.0 * cm, hoehe_start - (25 * cm), 'Sprung:')

                    p.drawString(15.0 * cm, hoehe_start - (24 * cm), str(ergebnis.ergebnis_boden_s))
                    p.drawString(15.0 * cm, hoehe_start - (24.5 * cm), str(ergebnis.ergebnis_barren_s))
                    p.drawString(15.0 * cm, hoehe_start - (25 * cm), str(ergebnis.ergebnis_sprung_s))

                    rang = rang + 1

                    if medaille != "-":
                        p.setFont('DejaVuSans-Bold', 16)
                        p.drawCentredString(breite / 2, hoehe_start - (27 * cm), "Abzeichen: " + medaille)

                    p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Urkunden_Bezirksturnfest.pdf")


@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def report_meisterschaften(request):
    meisterschaften = Meisterschaften.objects.order_by('-meisterschaft_gender')
    konfiguration = Konfiguration.objects.get(id=1)

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

    for meisterschaft in meisterschaften:
        ergebnis = BezirksturnfestErgebnisse.objects.filter(
            ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(meisterschaft.meisterschaft_ab),
            ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(meisterschaft.meisterschaft_bis),
            ergebnis_teilnehmer__teilnehmer_gender=meisterschaft.meisterschaft_gender
        ).order_by('-ergebnis_summe').first()

        if ergebnis:
            p.setFont('DejaVuSans-Bold', 18)

            p.setFont('DejaVuSans-Bold', 18)
            p.drawCentredString(breite / 2, hoehe_start - (20 * cm),
                                str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname) + " " +
                                str(ergebnis.ergebnis_teilnehmer.teilnehmer_name))

            p.setFont('DejaVuSans', 18)
            p.drawCentredString(breite / 2, hoehe_start - (21 * cm),
                                str(ergebnis.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))

            p.drawCentredString(breite / 2, hoehe_start - (22 * cm),
                                "hat mit " + str(ergebnis.ergebnis_summe) + " Punkten die:")

            p.setFont('DejaVuSans-Bold', 18)
            p.drawCentredString(breite / 2, hoehe_start - (23 * cm),
                                str(meisterschaft.meisterschaft))
            p.drawCentredString(breite / 2, hoehe_start - (24 * cm),
                                str(meisterschaft.get_meisterschaft_gender_display()))

            p.setFont('DejaVuSans', 18)
            p.drawCentredString(breite / 2, hoehe_start - (25 * cm),
                                "gewonnen.")

            #p.drawCentredString(breite / 2, hoehe_start - (23 * cm),
            #                    " *" + str(
            #                        datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr), "%Y-%m-%d").year))

            p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Urkunden_Meisterschaften.pdf")


@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def report_auswertung_vereine(request):
    konfiguration = Konfiguration.objects.get(id=1)

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Holen der Seitenabmessung
    breite, hoehe = landscape(A4)

    vereine = Vereine.objects.filter(verein_aktiv=True)

    for verein in vereine:

        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), konfiguration.bezirksturnfest + " " + str(konfiguration.jahr))
        h = h + 1
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste " + str(verein))
        h = h + 1

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 29.0 * cm, 0.6 * cm, stroke=0, fill=1)

        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
        p.drawString(4.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Jahrgang')
        p.drawString(8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
        p.drawString(11 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
        p.drawString(14 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
        p.drawString(17 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
        p.drawString(20 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
        p.drawString(23 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
        p.drawString(26 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')
        p.drawString(27.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Medaille')

        ergebnisse = (BezirksturnfestErgebnisse.objects.filter(ergebnis_teilnehmer__teilnehmer_verein=verein).
                      order_by('ergebnis_teilnehmer__teilnehmer_geburtsjahr'))
        #print(ergebnisse)
        for ergebnis in ergebnisse:
            h = h + 0.4
            jahr = datetime.strptime(str(ergebnis.ergebnis_teilnehmer.teilnehmer_geburtsjahr), "%Y-%m-%d").year
            p.drawString(0.5 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_teilnehmer.teilnehmer_name) + " " +
                         str(ergebnis.ergebnis_teilnehmer.teilnehmer_vorname))
            p.drawRightString(5.5 * cm, hoehe - (h * cm), str(jahr))

            p.drawRightString(8.1 * cm, hoehe - (h * cm), "(" + str(ergebnis.ergebnis_sprung_a) + "/" + str(ergebnis.ergebnis_sprung_b) +")")
            p.drawRightString(9 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))

            p.drawRightString(11.1 * cm, hoehe - (h * cm), "(" + str(ergebnis.ergebnis_mini_a) + "/" + str(ergebnis.ergebnis_mini_b) +")")
            p.drawRightString(12 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))

            p.drawRightString(14.1 * cm, hoehe - (h * cm), "(" + str(ergebnis.ergebnis_reck_a) + "/" + str(ergebnis.ergebnis_reck_b) +")")
            p.drawRightString(15 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))

            p.drawRightString(17.1 * cm, hoehe - (h * cm), "(" + str(ergebnis.ergebnis_balken_a) + "/" + str(ergebnis.ergebnis_balken_b) +")")
            p.drawRightString(18 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))

            p.drawRightString(20.1 * cm, hoehe - (h * cm), "(" + str(ergebnis.ergebnis_barren_a) + "/" + str(ergebnis.ergebnis_barren_b) +")")
            p.drawRightString(21 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))

            p.drawRightString(23.1 * cm, hoehe - (h * cm), "(" + str(ergebnis.ergebnis_boden_a) + "/" + str(ergebnis.ergebnis_boden_b) +")")
            p.drawRightString(24 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))

            summe_a = (ergebnis.ergebnis_sprung_a +
                       ergebnis.ergebnis_mini_a +
                       ergebnis.ergebnis_reck_a +
                       ergebnis.ergebnis_balken_a +
                       ergebnis.ergebnis_barren_a +
                       ergebnis.ergebnis_boden_a)

            summe_b = (ergebnis.ergebnis_sprung_b +
                       ergebnis.ergebnis_mini_b +
                       ergebnis.ergebnis_reck_b +
                       ergebnis.ergebnis_balken_b +
                       ergebnis.ergebnis_barren_b +
                       ergebnis.ergebnis_boden_b)

            p.drawRightString(26.1 * cm, hoehe - (h * cm), "(" + str(summe_a) + "/" + str(summe_b) +")")
            p.drawRightString(27 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))

            if 16 <= ergebnis.ergebnis_summe < 48:
                medaille = 'Bronze'
            elif 48 <= ergebnis.ergebnis_summe < 64:
                medaille = 'Silber'
            elif ergebnis.ergebnis_summe >= 64:
                medaille = 'Gold'
            else:
                medaille = "-"
            p.drawRightString(28.5 * cm, hoehe - (h * cm), str(medaille))
            if h > 24:
                p.showPage()
                h = 1
        p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Ergebnislisten_Vereine.pdf")


##########################################################################
# Area Löschen Bezirksturnfest
##########################################################################

@login_required
@permission_required('turnfest.view_bezirksturnfestergebnisse')
def delete_tables_bezirksturnfest(request):
    if request.method == 'POST':
        count_ergebnisse = BezirksturnfestErgebnisse.objects.all().delete()
        count_teilnehmer = Teilnehmer.objects.all().delete()
        #Teilnehmer.objects.raw("ALTER TABLE turnfest_teilnehmer AUTO_INCREMENT = 1;")
        #count_vereine = Vereine.objects.all().delete()
        #UPDATE sqlite_sequence SET seq = (SELECT MAX(col) FROM Tbl) WHERE name="Tbl"
        #print(count_teilnehmer)

        #Autoincrement Feld zurücksetzen
        if connection.vendor == 'sqlite':
            with connection.cursor() as cursor:
                cursor.execute("UPDATE sqlite_sequence SET seq = "
                               "(SELECT MAX(id) FROM 'turnfest_teilnehmer') WHERE name='turnfest_teilnehmer'")
                cursor.execute("UPDATE sqlite_sequence SET seq = "
                               "(SELECT MAX(id) FROM 'turnfest_bezirksturnfestergebnisse') "
                               "WHERE name='turnfest_bezirksturnfestergebnisse'")
        elif connection.vendor == 'mysql':
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE turnfest_teilnehmer AUTO_INCREMENT = 1;")

        return redirect('/turnfest/teilnehmer_list/')
    else:
        pass

    form = TablesDeleteForm()
    return render(request, 'turnfest/tables_delete.html', {'form': form})
