from django import forms
from django.core.exceptions import ValidationError

from .models import Vereine, Teilnehmer, Ligen, LigaturnenErgebnisse, Geraete


class UploadFileForm(forms.Form):
    file = forms.FileField()


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


class LigaErfassenForm(forms.ModelForm):
    class Meta:
        model = Ligen
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LigaErfassenForm, self).__init__(*args, **kwargs)

        # Ändere die Labels hier
        self.fields['liga'].label = 'Liga:'
        self.fields['liga_ab'].label = 'ab:'
        self.fields['liga_bis'].label = 'bis:'


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
        self.fields['teilnehmer_liga_tag'].label = 'Ligatag:'
        self.fields['teilnehmer_liga'].label = 'Liga:'
        self.fields['teilnehmer_mannschaft'].label = 'Mannschaft:'
        self.fields['teilnehmer_sprung'].label = 'Meldung Sprung:'
        self.fields['teilnehmer_mini'].label = 'Meldung Minitrampolin:'
        self.fields['teilnehmer_reck_stufenbarren'].label = 'Meldung Reck/Stufenbarren:'
        self.fields['teilnehmer_balken'].label = 'Meldung Balken:'
        self.fields['teilnehmer_barren'].label = 'Meldung Barren:'
        self.fields['teilnehmer_boden'].label = 'Meldung Boden:'


class ErgebnisTeilnehmerSuchen(forms.Form):

    startnummer = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'autofocus': 'autofocus',
            'autocomplete': 'off'
        }
    ),
        required=True
    )

    geraet = forms.ModelChoiceField(queryset=Geraete.objects.all(), label="", widget=forms.Select(
        attrs={
            'class': 'form-control'
        }
    ))


class ErgebnisTeilnehmererfassenForm(forms.ModelForm):

    ergebnis_sprung_a = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_sprung_b = forms.DecimalField(
        required=False,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'autofocus': 'autofocus',
            }
        ))

    ergebnis_mini_a = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_mini_b = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'autofocus': 'autofocus',
            }
        ))

    ergebnis_reck_a = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_reck_b = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'autofocus': 'autofocus',
            }
        ))

    ergebnis_balken_a = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_balken_b = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'autofocus': 'autofocus',
            }
        ))

    ergebnis_barren_a = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_barren_b = forms.DecimalField(
        required=False,
        initial=0.00,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'autofocus': 'autofocus',
            }
        ))

    ergebnis_boden_a = forms.DecimalField(
        required=False,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'autofocus': 'autofocus'
            }
        ))

    ergebnis_boden_b = forms.DecimalField(
        required=False,
        max_value=10,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        ))

    ergebnis_sprung_s = forms.DecimalField(
        disabled=True,
        required=False,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_mini_s = forms.DecimalField(
        disabled=True,
        required=False,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_reck_s = forms.DecimalField(
        disabled=True,
        required=False,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_balken_s = forms.DecimalField(
        disabled=True,
        required=False,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_barren_s = forms.DecimalField(
        disabled=True,
        required=False,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_boden_s = forms.DecimalField(
        disabled=True,
        required=False,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    ergebnis_summe = forms.DecimalField(
        disabled=True,
        required=False,
        initial=0.00,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ))

    def clean(self):
        cleaned_data = super().clean()
        ergebnis_sprung_a = cleaned_data.get('ergebnis_sprung_a')
        ergebnis_sprung_s = cleaned_data.get('ergebnis_sprung_s')
        ergebnis_reck_a = cleaned_data.get('ergebnis_reck_a')
        ergebnis_reck_s = cleaned_data.get('ergebnis_reck_s')
        ergebnis_mini_a = cleaned_data.get('ergebnis_mini_a')
        ergebnis_mini_s = cleaned_data.get('ergebnis_mini_s')
        ergebnis_balken_a = cleaned_data.get('ergebnis_balken_a')
        ergebnis_balken_s = cleaned_data.get('ergebnis_balken_s')
        ergebnis_barren_a = cleaned_data.get('ergebnis_barren_a')
        ergebnis_barren_s = cleaned_data.get('ergebnis_barren_s')
        ergebnis_boden_a = cleaned_data.get('ergebnis_boden_a')
        ergebnis_boden_s = cleaned_data.get('ergebnis_boden_s')

        anzahl_geraete = 0
        if ergebnis_sprung_s > 0.00:
            anzahl_geraete = anzahl_geraete + 1
        else:
            if ergebnis_sprung_a:
                anzahl_geraete = anzahl_geraete + 1

        if ergebnis_reck_s > 0.00:
            anzahl_geraete = anzahl_geraete + 1
        else:
            if ergebnis_reck_a:
                anzahl_geraete = anzahl_geraete + 1

        if ergebnis_mini_s > 0:
            anzahl_geraete = anzahl_geraete + 1
        else:
            if ergebnis_mini_a:
                anzahl_geraete = anzahl_geraete + 1

        if ergebnis_balken_s > 0:
            anzahl_geraete = anzahl_geraete + 1
        else:
            if ergebnis_balken_a:
                anzahl_geraete = anzahl_geraete + 1

        if ergebnis_barren_s > 0:
            anzahl_geraete = anzahl_geraete + 1
        else:
            if ergebnis_barren_a:
                anzahl_geraete = anzahl_geraete + 1

        if ergebnis_boden_s > 0:
            anzahl_geraete = anzahl_geraete + 1
        else:
            if ergebnis_boden_a:
                anzahl_geraete = anzahl_geraete + 1

        if anzahl_geraete > 4:
            raise ValidationError("Es wurden Ergebnisse für mehr als 4 Geräte erfasst! Dat kan net sin!")

    class Meta:
        model = LigaturnenErgebnisse
        fields = ['ergebnis_teilnehmer',
                  'ergebnis_ligatag',
                  'ergebnis_sprung_a',
                  'ergebnis_sprung_b',
                  'ergebnis_mini_a',
                  'ergebnis_mini_b',
                  'ergebnis_reck_a',
                  'ergebnis_reck_b',
                  'ergebnis_balken_a',
                  'ergebnis_balken_b',
                  'ergebnis_barren_a',
                  'ergebnis_barren_b',
                  'ergebnis_boden_a',
                  'ergebnis_boden_b',
                  'ergebnis_sprung_s',
                  'ergebnis_mini_s',
                  'ergebnis_reck_s',
                  'ergebnis_balken_s',
                  'ergebnis_barren_s',
                  'ergebnis_boden_s',
                  'ergebnis_summe',
                  ]


class TablesDeleteForm(forms.Form):
    pass
