from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import BezirksturnfestErgebnisse, Vereine, Teilnehmer


class UploadFileForm(forms.Form):
    file = forms.FileField()


class ErgebnisTeilnehmerSuchen(forms.Form):
    startnummer = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'autofocus': 'autofocus'
        }
    ),
        required=True
    )


class ErgebnisTeilnehmererfassen(forms.ModelForm):

    class Meta:
        model = BezirksturnfestErgebnisse
        fields = '__all__'


class VereinErfassenForm(forms.ModelForm):

    class Meta:
        model = Vereine
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VereinErfassenForm, self).__init__(*args, **kwargs)

        # Ändere die Labels hier
        self.fields['verein_name'].label = 'Vereinsname:'
        self.fields['verein_name_kurz'].label = 'Kurzbezeichnung:'
        self.fields['verein_strasse'].label = 'Strasse:'
        self.fields['verein_plz'].label = 'PLZ:'
        self.fields['verein_ort'].label = 'Ort:'
        self.fields['verein_telefon'].label = 'Telefon:'
        self.fields['verein_email'].label = 'E-Mail:'


class TeilnehmerErfassenForm(forms.ModelForm):

    class Meta:
        model = Teilnehmer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TeilnehmerErfassenForm, self).__init__(*args, **kwargs)

        # Ändere die Labels hier
        self.fields['teilnehmer_name'].label = 'Name:'
        self.fields['teilnehmer_vorname'].label = 'Vorname:'
        self.fields['teilnehmer_geburtsjahr'].label = 'Geburtsdatum:'
        self.fields['teilnehmer_gender'].label = 'Geschlecht:'
        self.fields['teilnehmer_verein'].label = 'Verein:'
        self.fields['teilnehmer_anwesend'].label = 'Anwesend:'
        self.fields['teilnehmer_sprung'].label = 'Meldung Sprung:'
        self.fields['teilnehmer_mini'].label = 'Meldung Minitrampolin:'
        self.fields['teilnehmer_reck_stufenbarren'].label = 'Meldung Reck/Stufenbarren:'
        self.fields['teilnehmer_balken'].label = 'Meldung Balken:'
        self.fields['teilnehmer_barren'].label = 'Meldung Barren:'
        self.fields['teilnehmer_boden'].label = 'Meldung Boden:'
