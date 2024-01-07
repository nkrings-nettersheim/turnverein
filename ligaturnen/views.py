import pandas as pd
import io

from django.shortcuts import render
from datetime import datetime, timezone

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

from .models import Vereine, Teilnehmer, Ligen, Geraete, LigaturnenErgebnisse, LigaturnenErgebnisseZwischenLiga, \
    LigaTag, LigaturnenErgebnisseZwischenEinzel
from .forms import VereinErfassenForm, LigaErfassenForm, TeilnehmerErfassenForm, UploadFileForm, \
    ErgebnisTeilnehmererfassenForm, ErgebnisTeilnehmerSuchen, TablesDeleteForm


def index(request):
    return render(request, 'ligaturnen/index.html')


def impressum(request):
    return render(request, 'ligaturnen/impressum.html')


def datenschutz(request):
    return render(request, 'ligaturnen/datenschutz.html')


def ligawettkampf(request):
    teilnehmer_1 = Teilnehmer.objects.filter(teilnehmer_liga_tag="1").count()
    teilnehmer_2 = Teilnehmer.objects.filter(teilnehmer_liga_tag="2").count()
    teilnehmer_3 = Teilnehmer.objects.filter(teilnehmer_liga_tag="3").count()

    dashboard = {}
    dashboard["teilnehmer_1"]= teilnehmer_1
    dashboard["teilnehmer_2"]= teilnehmer_2
    dashboard["teilnehmer_3"]= teilnehmer_3

    return render(request, 'ligaturnen/ligawettkampf.html', {'dashboard': dashboard})


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
    model = LigaTag
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

    #def get(request, *args, **kwargs):
        #print(args["WSGIRequest"])
    #    print(request.session['count_negativ'])
        #count_negativ = args.GET
    #    assert False

    #    print("Hallo" + str(count_negativ))
    #    return count_negativ

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


class LigaTagUpdateView(UpdateView):
    model = LigaTag
    template_name = "ligaturnen/ligatag_update.html"
    fields = '__all__'
    success_url = "/ligaturnen/ligawettkampf/"


def teilnehmer_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            countdict = handle_uploaded_file(request.FILES['file'])
            request.session['count_positiv'] = str(countdict["count_positiv"])
            request.session['count_negativ'] = str(countdict["count_negativ"])
            return redirect('/ligaturnen/teilnehmer_list/')
    else:
        form = UploadFileForm()
    return render(request, 'ligaturnen/teilnehmer_upload.html', {'form': form})


def handle_uploaded_file(file):
    # Lese die Daten aus der Excel-Datei
    df = pd.read_excel(file)
    # Iteriere durch die Zeilen und speichere die Daten in der Datenbank
    count_positiv = 0
    count_negativ = 0
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
            count_positiv = count_positiv + 1
        except:
            count_negativ = count_negativ + 1
            pass

    countdict = {"count_positiv": count_positiv, "count_negativ": count_negativ}
    #print(str(count_positiv) + " " + str(count_negativ))
    return countdict

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
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_sprung'
                                                      )

            elif geraet.geraet_db_name == "teilnehmer_mini":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_mini__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_sprung'
                                                      )
            elif geraet.geraet_db_name == "teilnehmer_reck_stufenbarren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_reck_stufenbarren__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_sprung'
                                                      )
            elif geraet.geraet_db_name == "teilnehmer_balken":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_balken__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_sprung'
                                                      )
            elif geraet.geraet_db_name == "teilnehmer_barren":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_barren__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
                                                      'teilnehmer_name',
                                                      'teilnehmer_vorname',
                                                      'teilnehmer_verein__verein_name_kurz',
                                                      'teilnehmer_geburtsjahr',
                                                      'teilnehmer_sprung'
                                                      )
            elif geraet.geraet_db_name == "teilnehmer_boden":
                teilnehmer_alle = Teilnehmer.objects.filter(
                    teilnehmer_boden__gt=0,
                    teilnehmer_liga_tag=ligaTag,
                    teilnehmer_liga=liga).values_list('id',
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

            content.append(Paragraph(liga.liga + "-Liga " + geraet.geraet_name + " Ligatag: " + str(ligaTag),
                                     styles['CenterAlign14']))
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
        geraete_id = request.POST['geraet']
        teilnehmer = Teilnehmer.objects.get(id=startnummer)
        ligatag = LigaTag.objects.get(id=1)
        # geraet = Geraete.objects.get(id=geraete_id)
        if teilnehmer:
            try:
                ergebnis = LigaturnenErgebnisse.objects.get(ergebnis_teilnehmer=startnummer)
                return redirect("/ligaturnen/edit/ergebnis/" + str(ergebnis.id) + '/?geraet=' + str(geraete_id) + "&ligatag=" + str(ligatag))
            except:
                return redirect("/ligaturnen/add/ergebnis" + "/?start=" + startnummer + "&geraet=" + str(geraete_id) + "&ligatag=" + str(ligatag))

        else:
            form = ErgebnisTeilnehmerSuchen()
            return render(request, 'ligaturnen/ergebnis_erfassen_suche.html', {'form': form})

    else:
        geraet_option = request.GET.get('geraet')
        teilnehmer_id = request.GET.get('teilnehmer')
        if teilnehmer_id:
            ergebnis = LigaturnenErgebnisse.objects.get(id=teilnehmer_id)
        else:
            ergebnis = ""
        form = ErgebnisTeilnehmerSuchen()
        form.geraet_option = geraet_option

    return render(request, 'ligaturnen/ergebnis_erfassen_suche.html', {'form': form, 'ergebnis': ergebnis})


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
            geraet = request.GET.get('geraet')
            return redirect('/ligaturnen/ergebnis_erfassen_suche/?geraet=' + geraet + "&teilnehmer=" + str(item.id))
        else:
            for field in form:
                print("Field Error:", field.name, field.errors)
    else:
        startnummer = request.GET.get('start')
        geraete_id = request.GET.get('geraet')
        teilnehmer = Teilnehmer.objects.get(id=startnummer)
        ligatag = LigaTag.objects.get(id=1)

        form = ErgebnisTeilnehmererfassenForm()
        form.turnerin = teilnehmer.teilnehmer_name + " " + teilnehmer.teilnehmer_vorname
        form.teilnehmer_id = teilnehmer.id
        form.geraet = geraete_id
        form.ligatag = ligatag
        form.add = True  # Damit im Formular die hidden Felder eingeblendet werden
    return render(request, 'ligaturnen/ergebnis_erfassen.html', {'form': form})


def edit_ergebnis(request, id=None):
    item = get_object_or_404(LigaturnenErgebnisse, id=id)
    form = ErgebnisTeilnehmererfassenForm(request.POST or None, instance=item)

    if form.is_valid():
        form.save()
        geraet = request.GET.get('geraet')
        # assert False
        return redirect('/ligaturnen/ergebnis_erfassen_suche/?geraet=' + geraet + "&teilnehmer=" + id)

    ligatag = LigaTag.objects.get(id=1)
    form.id = item.id
    form.turnerin = item.ergebnis_teilnehmer
    form.teilnehmer_id = item.ergebnis_teilnehmer.id
    form.geraet = request.GET.get('geraet')
    form.ligatag = ligatag
    # assert False
    return render(request, 'ligaturnen/ergebnis_erfassen.html', {'form': form})


##########################################################################
# Area Auswertung Ligaturnen Mannschaften
##########################################################################

def report_auswertung_mannschaft(request):
    ligen = Ligen.objects.all()
    vereine = Vereine.objects.all()
    geraete = Geraete.objects.all()
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

    # Ermittlung der Ergebnisse für die Mannschaften und speichern in der Zwischentabelle
    count_zwischenergebnisse = LigaturnenErgebnisseZwischenLiga.objects.all().delete()

    for liga in ligen:
        for verein in vereine:
            for mannschaft in range(3):
                for gen in gender:
                    sprung = 0
                    mini = 0
                    reck = 0
                    barren = 0
                    balken = 0
                    boden = 0

                    try:
                        erg_sprung = LigaturnenErgebnisse.objects.filter(
                            ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                            ergebnis_teilnehmer__teilnehmer_verein=verein,
                            ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                            ergebnis_teilnehmer__teilnehmer_ak=False,
                            ergebnis_teilnehmer__teilnehmer_gender=gen
                        ).order_by('-ergebnis_sprung_s')[:3]
                        if erg_sprung:
                            for erg in erg_sprung:
                                sprung = erg.ergebnis_sprung_s + sprung
                    except:
                        pass

                    try:
                        erg_mini = LigaturnenErgebnisse.objects.filter(
                            ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                            ergebnis_teilnehmer__teilnehmer_verein=verein,
                            ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                            ergebnis_teilnehmer__teilnehmer_ak=False,
                            ergebnis_teilnehmer__teilnehmer_gender = gen
                        ).order_by('-ergebnis_mini_s')[:3]
                        if erg_mini:
                            for erg in erg_mini:
                                mini = erg.ergebnis_mini_s + mini
                    except:
                        pass

                    try:
                        erg_reck = LigaturnenErgebnisse.objects.filter(
                            ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                            ergebnis_teilnehmer__teilnehmer_verein=verein,
                            ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                            ergebnis_teilnehmer__teilnehmer_ak=False,
                            ergebnis_teilnehmer__teilnehmer_gender=gen
                        ).order_by('-ergebnis_reck_s')[:3]
                        if erg_reck:
                            for erg in erg_reck:
                                reck = erg.ergebnis_reck_s + reck
                    except:
                        pass

                    try:
                        erg_barren = LigaturnenErgebnisse.objects.filter(
                            ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                            ergebnis_teilnehmer__teilnehmer_verein=verein,
                            ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                            ergebnis_teilnehmer__teilnehmer_ak=False,
                            ergebnis_teilnehmer__teilnehmer_gender=gen
                        ).order_by('-ergebnis_barren_s')[:3]
                        if erg_barren:
                            for erg in erg_barren:
                                barren = erg.ergebnis_barren_s + barren
                    except:
                        pass

                    try:
                        erg_balken = LigaturnenErgebnisse.objects.filter(
                            ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                            ergebnis_teilnehmer__teilnehmer_verein=verein,
                            ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                            ergebnis_teilnehmer__teilnehmer_ak=False,
                            ergebnis_teilnehmer__teilnehmer_gender=gen
                        ).order_by('-ergebnis_balken_s')[:3]
                        if erg_balken:
                            for erg in erg_balken:
                                balken = erg.ergebnis_balken_s + balken
                    except:
                        pass

                    try:
                        erg_boden = LigaturnenErgebnisse.objects.filter(
                            ergebnis_teilnehmer__teilnehmer_liga=str(liga.liga),
                            ergebnis_teilnehmer__teilnehmer_verein=verein,
                            ergebnis_teilnehmer__teilnehmer_mannschaft=mannschaft,
                            ergebnis_teilnehmer__teilnehmer_ak=False,
                            ergebnis_teilnehmer__teilnehmer_gender=gen
                        ).order_by('-ergebnis_boden_s')[:3]
                        if erg_boden:
                            for erg in erg_boden:
                                boden = erg.ergebnis_boden_s + boden
                    except:
                        pass

                    erg_summe = sprung + mini + reck + barren + balken + boden

                    if erg_summe > 0:
                        mannschaftergebnis = LigaturnenErgebnisseZwischenLiga(
                            liga=liga,
                            verein=verein,
                            mannschaft=mannschaft,
                            gender=gen,
                            ergebnis_sprung_s=sprung,
                            ergebnis_mini_s=mini,
                            ergebnis_reck_s=reck,
                            ergebnis_balken_s=balken,
                            ergebnis_barren_s=barren,
                            ergebnis_boden_s=boden
                        )

                        try:
                            mannschaftergebnis.save()
                        except:
                            pass

    # assert False
    for gen in gender:
        for liga in ligen:
            ergebnisse = LigaturnenErgebnisseZwischenLiga.objects.filter(liga=liga, gender=gen).order_by('-ergebnis_summe')

            if ergebnisse:
                # assert False
                h = 1
                p.setFont('DejaVuSans-Bold', 18)
                p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Ligaturnen, Mannschaft 2024")
                h = h + 0.8
                p.setFont('DejaVuSans-Bold', 14)
                if gen == 'w':
                    gen_lang = 'weiblich'
                else:
                    gen_lang = 'männlich'

                p.drawCentredString(breite / 2, hoehe - (h * cm), liga.liga + "-Liga, " + gen_lang)
                h = h + 1

                p.setFont('DejaVuSans', 8)

                p.setFillGray(0.75)
                p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)

                p.setFillGray(0.0)
                p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Rang')
                p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Mannschaft')
                p.drawString(4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
                p.drawString(8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
                p.drawString(9.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
                p.drawString(11.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
                p.drawString(12.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
                p.drawString(14.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
                p.drawString(16.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
                p.drawString(17.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')

                h = h + 0.5
                rang = 1
                ergebnis_summe_vorheriger = 0
                for ergebnis in ergebnisse:
                    if ergebnis_summe_vorheriger == ergebnis.ergebnis_summe:
                        rang = rang - 1
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))
                        rang = rang + 1
                    else:
                        p.drawString(0.5 * cm, hoehe - (h * cm), str(rang))

                    p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.mannschaft) + ". Mannschaft")
                    p.drawString(4.0 * cm, hoehe - (h * cm), str(ergebnis.verein))
                    p.drawString(8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
                    p.drawString(9.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
                    p.drawString(11.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
                    p.drawString(12.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
                    p.drawString(14.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
                    p.drawString(16.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
                    p.drawString(17.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))
                    ergebnis_summe_vorheriger = ergebnis.ergebnis_summe
                    h = h + 0.5
                    rang = rang + 1

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

    count_zwischenergebnisse = LigaturnenErgebnisseZwischenEinzel.objects.all().delete()

    gender = ['w', 'm']
    liga = "A"
    #gen = "w"
    #print(str(liga) + " " + str(gen))
    for gen in gender:
        #for liga in ligen:
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
                        # print(str(teilnehmer.teilnehmer_name) + " " + (str(sprung_zwischen)))
                        teilnehmer_alias_1 = teilnehmer_alias_2
                except:
                    pass
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
                        # print(str(teilnehmer.teilnehmer_name) + " " + (str(sprung_zwischen)))
                        teilnehmer_alias_1 = teilnehmer_alias_2
                except:
                    pass

            summe_zwischen = sprung_zwischen + mini_zwischen + reck_zwischen + balken_zwischen + barren_zwischen + boden_zwischen
            if summe_zwischen >0:
                obj, created = LigaturnenErgebnisseZwischenEinzel.objects.update_or_create(
                    teilnehmer_name=teilnehmer.teilnehmer_name,
                    teilnehmer_vorname=teilnehmer.teilnehmer_vorname,
                    teilnehmer_geburtsjahr=teilnehmer.teilnehmer_geburtsjahr,
                    teilnehmer_gender=teilnehmer.teilnehmer_gender,
                    teilnehmer_verein=teilnehmer.teilnehmer_verein,
                    defaults={"teilnehmer_name": teilnehmer.teilnehmer_name,
                              "teilnehmer_vorname": teilnehmer.teilnehmer_vorname,
                              "teilnehmer_geburtsjahr": teilnehmer.teilnehmer_geburtsjahr,
                              "teilnehmer_gender": teilnehmer.teilnehmer_gender,
                              "teilnehmer_verein": teilnehmer.teilnehmer_verein,
                              "ergebnis_sprung_s": sprung_zwischen,
                              "ergebnis_mini_s": mini_zwischen,
                              "ergebnis_reck_s": reck_zwischen,
                              "ergebnis_balken_s": balken_zwischen,
                              "ergebnis_barren_s": barren_zwischen,
                              "ergebnis_boden_s": boden_zwischen,
                              "ergebnis_summe": summe_zwischen
                              }

            )

                #print(str(teilnehmer.teilnehmer_name) + " " + (str(sprung_zwischen)))

    for gen in gender:

        ergebnisse = LigaturnenErgebnisseZwischenEinzel.objects.filter(
            teilnehmer_gender=gen
        ).order_by('teilnehmer_geburtsjahr', '-ergebnis_summe')

        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Ligaturnen 2024")
        h = h + 0.8
        p.setFont('DejaVuSans-Bold', 14)
        p.drawCentredString(breite / 2, hoehe - (h * cm), gen)
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
        #p.drawString(19.3 * cm, hoehe - (h * cm) + 0.2 * cm, 'Medaillie')

        jahr_2 = ""
        rang = 1
        ergebnis_summe_vorheriger = 0
        for ergebnis in ergebnisse:
            jahr = datetime.strptime(str(ergebnis.teilnehmer_geburtsjahr), "%Y-%m-%d").year
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

            #if 16 <= ergebnis.ergebnis_summe < 48:
            #    medaille = 'Bronze'
            #elif 48 <= ergebnis.ergebnis_summe < 64:
            #    medaille = 'Silber'
            #elif ergebnis.ergebnis_summe >= 64:
            #    medaille = 'Gold'
            #else:
            #    medaille = "-"

            #p.drawString(19.3 * cm, hoehe - (h * cm), medaille)

            h = h + 0.5
            rang = rang + 1

        # if ergebnisse:
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

        # meister_innen = BezirksturnfestErgebnisse.objects.filter(
        #    ergebnis_teilnehmer__teilnehmer_geburtsjahr__gte=str(meisterschaft.meisterschaft_ab),
        #    ergebnis_teilnehmer__teilnehmer_geburtsjahr__lte=str(meisterschaft.meisterschaft_bis),
        #    ergebnis_teilnehmer__teilnehmer_gender=meisterschaft.meisterschaft_gender).order_by("-ergebnis_summe")
        #            assert False
        #            h = h + 0.5

        # i = 0  # zähler
        # ergebnis_zwischen = 0  # zwischenspeicherung des vorherigen ergebnisses
        # for meister_in in meister_innen:
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


##########################################################################
# Area Auswertung Vereine
##########################################################################
def report_auswertung_vereine(request):
    vereine = Vereine.objects.all()

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
        ergebnisse = LigaturnenErgebnisseZwischenEinzel.objects.filter(teilnehmer_verein=verein).order_by("-teilnehmer_gender", "teilnehmer_geburtsjahr", "teilnehmer_name")

        h = 1
        p.setFont('DejaVuSans-Bold', 18)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Ergebnisliste Ligaturnen 2024")
        h = h + 0.8

        p.setFont('DejaVuSans-Bold', 14)
        p.drawCentredString(breite / 2, hoehe - (h * cm), "Verein: " + str(verein))
        h = h + 1

        p.setFont('DejaVuSans', 8)

        p.setFillGray(0.75)
        p.rect(0.2 * cm, hoehe - (h * cm), 20.6 * cm, 0.6 * cm, stroke=0, fill=1)

        p.setFillGray(0.0)
        p.drawString(0.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Jahrg.')
        p.drawString(1.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'w/m')
        p.drawString(3.5 * cm, hoehe - (h * cm) + 0.2 * cm, 'Teilnehmer/in')
        p.drawString(7 * cm, hoehe - (h * cm) + 0.2 * cm, 'Verein')
        p.drawString(10 * cm, hoehe - (h * cm) + 0.2 * cm, 'Sprung')
        p.drawString(11.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Minitr.')
        p.drawString(13.2 * cm, hoehe - (h * cm) + 0.2 * cm, 'Reck/Stuf.')
        p.drawString(14.8 * cm, hoehe - (h * cm) + 0.2 * cm, 'Balken')
        p.drawString(16.4 * cm, hoehe - (h * cm) + 0.2 * cm, 'Barren')
        p.drawString(18.0 * cm, hoehe - (h * cm) + 0.2 * cm, 'Boden')
        p.drawString(19.6 * cm, hoehe - (h * cm) + 0.2 * cm, 'Gesamt')
        # p.drawString(19.3 * cm, hoehe - (h * cm) + 0.2 * cm, 'Medaillie')

        h = h + 0.5

        for ergebnis in ergebnisse:
            p.drawString(0.5 * cm, hoehe - (h * cm), str(datetime.strptime(str(ergebnis.teilnehmer_geburtsjahr), "%Y-%m-%d").year))
            p.drawString(1.5 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_gender))
            p.drawString(3.5 * cm, hoehe - (h * cm), str(ergebnis.teilnehmer_name) + " " +
                         str(ergebnis.teilnehmer_vorname))
            p.drawString(7.0 * cm, hoehe - (h * cm),
                         str(ergebnis.teilnehmer_verein.verein_name_kurz))
            p.drawString(10 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_sprung_s))
            p.drawString(11.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_mini_s))
            p.drawString(13.2 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_reck_s))
            p.drawString(14.8 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_balken_s))
            p.drawString(16.4 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_barren_s))
            p.drawString(18.0 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_boden_s))
            p.drawString(19.6 * cm, hoehe - (h * cm), str(ergebnis.ergebnis_summe))

            h = h + 0.5

        current_dateTime = datetime.now().strftime("%d.%m.%Y %H:%M Uhr")
        p.drawString(0.5 * cm, hoehe - (29 * cm), str(current_dateTime))

        p.showPage()  # Erzwingt eine neue Seite

    # Close the PDF object cleanly, and we're done.
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="Ergebnislisten_Vereine.pdf")


##########################################################################
# Area Verein Upload
##########################################################################

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


def delete_tables_ligaturnen(request):
    if request.method == 'POST':
        count_ergebnisse = LigaturnenErgebnisse.objects.all().delete()
        count_teilnehmer = Teilnehmer.objects.all().delete()
        # count_vereine = Vereine.objects.all().delete()
        # UPDATE sqlite_sequence SET seq = (SELECT MAX(col) FROM Tbl) WHERE name="Tbl"
        return redirect('/ligaturnen/teilnehmer_list/')
    else:
        pass

    form = TablesDeleteForm()
    return render(request, 'ligaturnen/tables_delete.html', {'form': form})
