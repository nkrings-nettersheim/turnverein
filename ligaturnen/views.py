import pandas as pd
import io

from django.shortcuts import render
from datetime import datetime

from django.conf import settings
from django.db.models import Count, DateField, DateTimeField
from django.db.models.functions import Cast, TruncDate
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.http import FileResponse

from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Frame
from reportlab.graphics.shapes import Line
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak, Spacer

from django.views import View
from weasyprint import HTML, CSS

from turnverein.settings import BASE_DIR

from .models import Vereine, Teilnehmer, Ligen, Geraete, LigaturnenErgebnisse
from .forms import VereinErfassenForm, LigaErfassenForm, TeilnehmerErfassenForm, UploadFileForm, \
    ErgebnisTeilnehmererfassenForm, ErgebnisTeilnehmerSuchen


def index(request):
    return render(request, 'ligaturnen/index.html')


def impressum(request):
    return render(request, 'ligaturnen/impressum.html')


def datenschutz(request):
    return render(request, 'ligaturnen/datenschutz.html')


def ligawettkampf(request):
    return render(request, 'ligaturnen/ligawettkampf.html')


##########################################################################
# Area Verein create and change
##########################################################################
class VereineCreateView(CreateView):
    model = Vereine
    template_name = "ligaturnen/vereine_create.html"
    form_class = VereinErfassenForm
    success_url = reverse_lazy("ligaturnen:vereine_list")


class VereineListView(ListView):
    model = Vereine


class VereineDetailView(DetailView):
    model = Vereine


class VereineUpdateView(UpdateView):
    model = Vereine
    template_name = "ligaturnen/vereine_update.html"
    fields = '__all__'
    success_url = "/ligaturnen/vereine_list/"


class VereineDeleteView(DeleteView):
    model = Vereine
    template_name = "ligaturnen/vereine_delete.html"
    success_url = reverse_lazy("ligaturnen:vereine_list")


def report_vereine(request):
    vereine = Vereine.objects.all()

    html_file = 'pdf_templates/report_vereine_ligaturnen.html'
    css_file = '/css/report_vereine.css'

    filename = "vereine_ligaturnen.pdf"

    html_string = render_to_string(html_file, {'vereine': vereine})

    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    pdf = html.write_pdf(stylesheets=[CSS(settings.STATIC_ROOT + css_file)])
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response


##########################################################################
# Area Ligen create and change
##########################################################################
class LigenCreateView(CreateView):
    model = Ligen
    template_name = "ligaturnen/ligen_create.html"
    form_class = LigaErfassenForm
    success_url = reverse_lazy("ligaturnen:ligen_list")


class LigenListView(ListView):
    model = Ligen


class LigenDetailView(DetailView):
    model = Ligen


class LigenUpdateView(UpdateView):
    model = Ligen
    template_name = "ligaturnen/ligen_update.html"
    fields = '__all__'
    success_url = "/ligaturnen/ligen_list/"


class LigenDeleteView(DeleteView):
    model = Ligen
    template_name = "ligaturnen/ligen_delete.html"
    success_url = reverse_lazy("ligaturnen:ligen_list")


##########################################################################
# Area Teilnehmer create and change
##########################################################################
class TeilnehmerCreateView(CreateView):
    model = Teilnehmer
    template_name = "ligaturnen/teilnehmer_create.html"
    form_class = TeilnehmerErfassenForm
    # fields = '__all__'
    success_url = reverse_lazy("ligaturnen:teilnehmer_list")


class TeilnehmerList(ListView):
    model = Teilnehmer

    ordering = ['teilnehmer_verein', '-teilnehmer_gender', 'teilnehmer_name']


class TeilnehmerDetailView(DetailView):
    model = Teilnehmer


class TeilnehmerUpdateView(UpdateView):
    model = Teilnehmer
    template_name = "ligaturnen/teilnehmer_update.html"
    # fields = '__all__'
    form_class = TeilnehmerErfassenForm
    success_url = reverse_lazy("ligaturnen:teilnehmer_list")


class TeilnehmerDeleteView(DeleteView):
    model = Teilnehmer
    template_name = "ligaturnen/teilnehmer_delete.html"
    success_url = reverse_lazy("ligaturnen:teilnehmer_list")


def teilnehmer_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('/ligaturnen/teilnehmer_list/')
    else:
        form = UploadFileForm()
    return render(request, 'ligaturnen/teilnehmer_upload.html', {'form': form})


def handle_uploaded_file(file):
    # Lese die Daten aus der Excel-Datei
    df = pd.read_excel(file)
    # assert False
    # Iteriere durch die Zeilen und speichere die Daten in der Datenbank
    for index, row in df.iterrows():
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
        except:
            pass


##########################################################################
# Area Download verschiedene Dokumente
##########################################################################

def download_document(request):
    if request.method == 'GET':
        file_name = request.GET.get('file_name')
        document_path = settings.MEDIA_ROOT + '/' + file_name
        response = FileResponse(open(document_path, 'rb'), as_attachment=True)
        return response

    return redirect('/ligaturnen/')


##########################################################################
# Area Geräteliste erzeugen
##########################################################################

def report_geraetelisten(request):
    ligen = Ligen.objects.all()
    geraete = Geraete.objects.all()

    # Definieren Sie die gewünschte Schriftart und laden Sie sie
    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

    font_path = BASE_DIR / "ttf/dejavu-sans/ttf/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", font_path))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Wettkampfliste_Ligaturnen.pdf"'
    # response['Content-Disposition'] = 'attachment; filename="Wettkampfliste_Ligaturnen.pdf"'

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
    teilnehmer_alle = []

    for liga in ligen:
        for geraet in geraete:

            if geraet.geraet_db_name == "teilnehmer_sprung":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_sprung__gt=0,
                    teilnehmer_geburtsjahr__range=[liga.liga_ab,
                                                   liga.liga_bis]).values_list('id',
                                                                               'teilnehmer_name',
                                                                               'teilnehmer_vorname',
                                                                               'teilnehmer_verein__verein_name_kurz',
                                                                               'teilnehmer_geburtsjahr',
                                                                               'teilnehmer_sprung'
                                                                               )

            elif geraet.geraet_db_name == "teilnehmer_mini":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_mini__gt=0,
                    teilnehmer_geburtsjahr__range=[liga.liga_ab,
                                                   liga.liga_bis]).values_list('id',
                                                                               'teilnehmer_name',
                                                                               'teilnehmer_vorname',
                                                                               'teilnehmer_verein__verein_name_kurz',
                                                                               'teilnehmer_geburtsjahr',
                                                                               'teilnehmer_sprung'
                                                                               )
            elif geraet.geraet_db_name == "teilnehmer_reck_stufenbarren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_reck_stufenbarren__gt=0,
                    teilnehmer_geburtsjahr__range=[liga.liga_ab,
                                                   liga.liga_bis]).values_list('id',
                                                                               'teilnehmer_name',
                                                                               'teilnehmer_vorname',
                                                                               'teilnehmer_verein__verein_name_kurz',
                                                                               'teilnehmer_geburtsjahr',
                                                                               'teilnehmer_sprung'
                                                                               )
            elif geraet.geraet_db_name == "teilnehmer_balken":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_balken__gt=0,
                    teilnehmer_geburtsjahr__range=[liga.liga_ab,
                                                   liga.liga_bis]).values_list('id',
                                                                               'teilnehmer_name',
                                                                               'teilnehmer_vorname',
                                                                               'teilnehmer_verein__verein_name_kurz',
                                                                               'teilnehmer_geburtsjahr',
                                                                               'teilnehmer_sprung'
                                                                               )
            elif geraet.geraet_db_name == "teilnehmer_barren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_barren__gt=0,
                    teilnehmer_geburtsjahr__range=[liga.liga_ab,
                                                   liga.liga_bis]).values_list('id',
                                                                               'teilnehmer_name',
                                                                               'teilnehmer_vorname',
                                                                               'teilnehmer_verein__verein_name_kurz',
                                                                               'teilnehmer_geburtsjahr',
                                                                               'teilnehmer_sprung'
                                                                               )
            elif geraet.geraet_db_name == "teilnehmer_boden":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_boden__gt=0,
                    teilnehmer_geburtsjahr__range=[liga.liga_ab,
                                                   liga.liga_bis]).values_list('id',
                                                                               'teilnehmer_name',
                                                                               'teilnehmer_vorname',
                                                                               'teilnehmer_verein__verein_name_kurz',
                                                                               'teilnehmer_geburtsjahr',
                                                                               'teilnehmer_sprung'
                                                                               )

            content.append(Paragraph('Ligaturnen 2024', styles['CenterAlign20']))
            content.append(Spacer(1, 4))

            # Add a line to the PDF
            content.append(Paragraph(
                "____________________________________________________________________________________________________",
                normal_style))
            content.append(Spacer(1, 4))

            content.append(Paragraph(liga.liga + " " + geraet.geraet_name, styles['CenterAlign14']))
            content.append(Spacer(1, 12))

            headers = ['Start-Nr.', 'Nachname', 'Vorname', 'Verein', 'Jahrgang', 'Meldung', 'A-Note', 'B-Note',
                       'Summe']
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

            content.append(PageBreak())

    pdf.build(content)

    return response


##########################################################################
# Area Ergebnisse erfassen
##########################################################################

def ergebnis_erfassen_suche(request):
    if request.method == "POST":
        startnummer = request.POST['startnummer']
        teilnehmer = Teilnehmer.objects.get(id=startnummer)
        if teilnehmer:
            try:
                ergebnis = LigaturnenErgebnisse.objects.get(ergebnis_teilnehmer=startnummer)
                return redirect("/ligaturnen/edit/ergebnis/" + str(ergebnis.id) + '/')
            except:
                return redirect("/ligaturnen/add/ergebnis" + "/?start=" + startnummer)

        else:
            form = ErgebnisTeilnehmerSuchen()
            return render(request, 'ligaturnen/ergebnis_erfassen_suche.html', {'form': form})

    else:
        form = ErgebnisTeilnehmerSuchen()

    return render(request, 'ligaturnen/ergebnis_erfassen_suche.html', {'form': form})


def ergebnis_erfassen(request):
    if request.method == "POST":
        pass

    else:
        form = ErgebnisTeilnehmerSuchen()

    return render(request, 'ligaturnen/ergebnis_erfassen_suche.html', {'form': form})


class ErgebnisCreateView(CreateView):
    model = LigaturnenErgebnisse
    template_name = "ligaturnen/ergebnis_erfassen.html"
    form_class = ErgebnisTeilnehmererfassenForm
    # fields = '__all__'
    success_url = reverse_lazy("ligaturnen:ergebnis_erfassen_suche")


class ErgebnisUpdateView(UpdateView):
    model = LigaturnenErgebnisse
    template_name = "ligaturnen/ergebnis_erfassen.html"
    form_class = ErgebnisTeilnehmererfassenForm
    success_url = reverse_lazy("ligaturnen:ergebnis_erfassen_suche")


def add_ergebnis(request):
    if request.method == "POST":
        form = ErgebnisTeilnehmererfassenForm(request.POST)
        # assert False
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
            return redirect('/ligaturnen/ergebnis_erfassen_suche/')
    else:
        startnummer = request.GET.get('start')
        teilnehmer = Teilnehmer.objects.get(id=startnummer)

        form = ErgebnisTeilnehmererfassenForm()
        form.turnerin = teilnehmer.teilnehmer_name + " " + teilnehmer.teilnehmer_vorname
        form.teilnehmer_id = teilnehmer.id
    return render(request, 'ligaturnen/ergebnis_erfassen.html', {'form': form})


def edit_ergebnis(request, id=None):
    item = get_object_or_404(LigaturnenErgebnisse, id=id)
    form = ErgebnisTeilnehmererfassenForm(request.POST or None, instance=item)
    # assert False
    if form.is_valid():
        form.save()
        return redirect('/ligaturnen/ergebnis_erfassen_suche/')

    form.id = item.id
    form.turnerin = item.ergebnis_teilnehmer
    form.teilnehmer_id = item.ergebnis_teilnehmer.id
    return render(request, 'ligaturnen/ergebnis_erfassen.html', {'form': form})


##########################################################################
# Area Auswertung Ligaturnen Mannschaften
##########################################################################

def report_auswertung_mannschaft(request):
    ligen = Ligen.objects.all()

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

    for liga in ligen:
        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Ligaturnen  Mannschaft 2024")
        h = h + 0.8
        p.setFont('DejaVuSans-Bold', 14)
        p.drawCentredString(breite / 2, hoehe - (h * cm), liga.liga )
        h = h + 1

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)

        p.setFillGray(0.0)

        current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
        p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

        p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="Ergebnislisten_Ligaturnen_Einzel.pdf")
##########################################################################
# Area Auswertung Ligaturnen Einzelturnerinnen
##########################################################################

def report_auswertung_einzel(request):
    ligen = Ligen.objects.all()

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

    gender = ['w', 'm']
    for liga in ligen:
        for gen in gender:
            ergebnisse = LigaturnenErgebnisse.objects.filter(
                ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(liga.liga_ab),
                ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(liga.liga_bis),
                ergebnis_teilnehmer__teilnehmer_gender=gen
            ).order_by('ergebnis_teilnehmer__teilnehmer_geburtsjahr', '-ergebnis_summe')

            h = 1
            p.setFont('DejaVuSans-Bold', 18)
            p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Ligaturnen 2024")
            h = h + 0.8
            p.setFont('DejaVuSans-Bold', 14)
            p.drawCentredString(breite / 2, hoehe - (h * cm), liga.liga + " " + gen)
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

            #if ergebnisse:
             #   h = h + 1
              #  p.line(0.2 * cm, hoehe - (h * cm), 20.8 * cm, hoehe - (h * cm))
#
 #               h = h + 1
  #              p.setFillColorRGB(1, 0.6, 0.8)
   #             p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)
#
 #               p.setFillGray(0.0)
  #              p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm,
   #                          liga.liga + " " + gen)

                #meister_innen = BezirksturnfestErgebnisse.objects.filter(
                #    ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(meisterschaft.meisterschaft_ab),
                #    ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(meisterschaft.meisterschaft_bis),
                #    ergebnis_teilnehmer__teilnehmer_gender=meisterschaft.meisterschaft_gender).order_by("-ergebnis_summe")
                #            assert False
    #            h = h + 0.5

                #i = 0  # zähler
                #ergebnis_zwischen = 0  # zwischenspeicherung des vorherigen ergebnisses
                #for meister_in in meister_innen:
                #    if i > 0:
                #        if ergebnis_zwischen == meister_in.ergebnis_summe:
                #            p.drawString(1.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_teilnehmer))
                #            p.drawString(5.0 * cm, hoehe - (h * cm),
                #                         str(meister_in.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))
                #            p.drawString(9.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_summe) + " " + "Punkte")
                #    else:
                #        p.drawString(1.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_teilnehmer))
                #        p.drawString(5.0 * cm, hoehe - (h * cm),
                #                     str(meister_in.ergebnis_teilnehmer.teilnehmer_verein.verein_name_kurz))
                #        p.drawString(9.5 * cm, hoehe - (h * cm), str(meister_in.ergebnis_summe) + " " + "Punkte")
   #
                #    ergebnis_zwischen = meister_in.ergebnis_summe
                #    i = i + 1
                #    h = h + 0.4

            current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
            p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

            p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="Ergebnislisten_Ligaturnen_Einzel.pdf")
