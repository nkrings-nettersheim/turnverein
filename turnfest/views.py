import io
import os
import pandas as pd

from django.conf import settings
from django.db.models import Count
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.http import FileResponse

from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from weasyprint import HTML, CSS

from turnverein.settings import BASE_DIR

from .models import Vereine, Teilnehmer, Wettkampfteilnahme, Geraete, Riegen
from .forms import UploadFileForm


##########################################################################
# Area allgemeine Seiten
##########################################################################
def index(request):
    return render(request, 'turnfest/index.html')


def bezirksturnfest(request):
    return render(request, 'turnfest/bezirksturnfest.html')


def ligawettkampf(request):
    return render(request, 'turnfest/ligawettkampf.html')


def impressum(request):
    return render(request, 'turnfest/impressum.html')


def datenschutz(request):
    return render(request, 'turnfest/datenschutz.html')


##########################################################################
# Area Verein create and change
##########################################################################
class VereineCreateView(CreateView):
    model = Vereine
    template_name = "turnfest/vereine_create.html"
    fields = '__all__'
    success_url = "/"


class VereineListView(ListView):
    model = Vereine


class VereineDetailView(DetailView):
    model = Vereine


class VereineUpdateView(UpdateView):
    model = Vereine
    template_name = "turnfest/vereine_update.html"
    fields = '__all__'
    success_url = "/turnfest/vereine_list/"


class VereineDeleteView(DeleteView):
    model = Vereine
    template_name = "turnfest/vereine_delete.html"
    success_url = reverse_lazy("turnfest:vereine_list")


def report_vereine(request):
    vereine = Vereine.objects.all()

    html_file = 'pdf_templates/report_vereine.html'
    css_file = '/css/report_vereine.css'

    filename = "vereine.pdf"

    html_string = render_to_string(html_file, {'vereine': vereine})

    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    pdf = html.write_pdf(stylesheets=[CSS(settings.STATIC_ROOT + css_file)])
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response


##########################################################################
# Area Teilnehmer create and change
##########################################################################
class TeilnehmerCreateView(CreateView):
    model = Teilnehmer
    template_name = "turnfest/teilnehmer_create.html"
    fields = '__all__'
    success_url = reverse_lazy("turnfest:teilnehmer_list")


class TeilnehmerList(ListView):
    model = Teilnehmer


class TeilnehmerDetailView(DetailView):
    model = Teilnehmer


class TeilnehmerUpdateView(UpdateView):
    model = Teilnehmer
    template_name = "turnfest/teilnehmer_update.html"
    fields = '__all__'
    success_url = reverse_lazy("turnfest:teilnehmer_list")


class TeilnehmerDeleteView(DeleteView):
    model = Teilnehmer
    template_name = "turnfest/teilnehmer_delete.html"
    success_url = reverse_lazy("turnfest:teilnehmer_list")


##########################################################################
# Area Wettkampfteilnehmer create and change
##########################################################################
class WettkampfteilnahmeCreateView(CreateView):
    model = Wettkampfteilnahme
    template_name = "turnfest/wettkampfteilnahme_create.html"
    fields = '__all__'
    success_url = "/"


class WettkampfteilnahmeList(ListView):
    model = Wettkampfteilnahme


class WettkampfteilnahmeDetailView(DetailView):
    model = Wettkampfteilnahme


class WettkampfteilnahmeUpdateView(UpdateView):
    model = Wettkampfteilnahme
    template_name = "turnfest/wettkampfteilnahme_update.html"
    fields = '__all__'
    success_url = "/"


##########################################################################
# Area Wettkampfteilnehmer create and change
##########################################################################

def report_geraetelisten(request):
    riegen = Riegen.objects.all()
    geraete = Geraete.objects.all()
    #teilnehmer_geburtsjahr_group = Teilnehmer.objects.values('teilnehmer_geburtsjahr').annotate(
    #    count=Count('teilnehmer_geburtsjahr'))

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

    for riege in riegen:
        for geraet in geraete:

            h = 2

            p.setFont('DejaVuSans-Bold', 18)
            p.drawCentredString(breite / 2, hoehe - (1 * cm), riege.riege + " " + geraet.geraet_name)


            if geraet.geraet_db_name == "teilnehmer_sprung":
                teilnehmer_alle = Teilnehmer.objects.filter(teilnehmer_sprung__gt=0,
                                                            teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                                                           riege.riege_bis])
            elif geraet.geraet_db_name == "teilnehmer_mini":
                teilnehmer_alle = Teilnehmer.objects.filter(teilnehmer_mini__gt=0,
                                                            teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                                                           riege.riege_bis])
            elif geraet.geraet_db_name == "teilnehmer_reck_stufenbarren":
                teilnehmer_alle = Teilnehmer.objects.filter(teilnehmer_reck_stufenbarren__gt=0,
                                                            teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                                                           riege.riege_bis])
            elif geraet.geraet_db_name == "teilnehmer_balken":
                teilnehmer_alle = Teilnehmer.objects.filter(teilnehmer_balken__gt=0,
                                                            teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                                                           riege.riege_bis])
            elif geraet.geraet_db_name == "teilnehmer_barren":
                teilnehmer_alle = Teilnehmer.objects.filter(teilnehmer_barren__gt=0,
                                                            teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                                                           riege.riege_bis])
            elif geraet.geraet_db_name == "teilnehmer_boden":
                teilnehmer_alle = Teilnehmer.objects.filter(teilnehmer_boden__gt=0,
                                                            teilnehmer_geburtsjahr__range=[riege.riege_ab,
                                                                                           riege.riege_bis])

            for teilnehmer in teilnehmer_alle:
                p.setFont('DejaVuSans', 12)
                h = h + 1

                p.drawString(2 * cm, hoehe - (h * cm), teilnehmer.teilnehmer_name)
                p.drawString(6 * cm, hoehe - (h * cm), teilnehmer.teilnehmer_vorname)
                p.drawString(10 * cm, hoehe - (h * cm), teilnehmer.teilnehmer_verein.verein_name_kurz)
                if geraet.geraet_db_name == "teilnehmer_sprung":
                    p.drawString(15 * cm, hoehe - (h * cm), str(teilnehmer.teilnehmer_sprung))
                elif geraet.geraet_db_name == "teilnehmer_mini":
                    p.drawString(15 * cm, hoehe - (h * cm), str(teilnehmer.teilnehmer_mini))
                elif geraet.geraet_db_name == "teilnehmer_reck_stufenbarren":
                    p.drawString(15 * cm, hoehe - (h * cm), str(teilnehmer.teilnehmer_reck_stufenbarren))
                elif geraet.geraet_db_name == "teilnehmer_balken":
                    p.drawString(15 * cm, hoehe - (h * cm), str(teilnehmer.teilnehmer_balken))
                elif geraet.geraet_db_name == "teilnehmer_barren":
                    p.drawString(15 * cm, hoehe - (h * cm), str(teilnehmer.teilnehmer_barren))
                elif geraet.geraet_db_name == "teilnehmer_boden":
                    p.drawString(15 * cm, hoehe - (h * cm), str(teilnehmer.teilnehmer_boden))

            p.showPage()  # Erzwingt eine neue Seite

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    # p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Wettkampfliste.pdf")


def teilnehmer_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('/turnfest/teilnehmer_list/')
    else:
        form = UploadFileForm()
    return render(request, 'turnfest/teilnehmer_upload.html', {'form': form})


def handle_uploaded_file(file):
    # Lese die Daten aus der Excel-Datei
    df = pd.read_excel(file)

    # Iteriere durch die Zeilen und speichere die Daten in der Datenbank
    for index, row in df.iterrows():
        Teilnehmer_neu = Teilnehmer(teilnehmer_name=row['Nachname'],
                                    teilnehmer_vorname=row['Vorname'],
                                    teilnehmer_gender=row['Geschlecht'],
                                    teilnehmer_geburtsjahr=row['Geburtsjahr'],
                                    teilnehmer_verein_id=row['Verein'],
                                    teilnehmer_anwesend="True",
                                    teilnehmer_sprung=row['Sprung'],
                                    teilnehmer_mini=row['Minitrampolin'],
                                    teilnehmer_reck_stufenbarren=row['Reck_Stufenbarren'],
                                    teilnehmer_balken=row['Schwebebalken'],
                                    teilnehmer_barren=row['Barren'],
                                    teilnehmer_boden=row['Boden'],
                                    )
        Teilnehmer_neu.save()
