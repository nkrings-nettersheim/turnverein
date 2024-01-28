from django.db import models
from django.core.validators import MaxValueValidator


class Vereine(models.Model):
    verein_name = models.CharField(max_length=75, blank=True, default='', null=True)
    verein_name_kurz = models.CharField(max_length=20, blank=True, default='', null=True)
    verein_strasse = models.CharField(max_length=100, blank=True, default='', null=True)
    verein_plz = models.CharField(max_length=5, blank=True, default='', null=True)
    verein_ort = models.CharField(max_length=100, blank=True, default='', null=True)
    verein_telefon = models.CharField(max_length=100, blank=True, default='', null=True)
    verein_email = models.EmailField(max_length=254, blank=True)

    def __str__(self):
        return self.verein_name_kurz


class Geraete(models.Model):
    geraet_name = models.CharField(max_length=30, blank=True, default='', null=True)
    geraet_db_name = models.CharField(max_length=30, blank=True, default='', null=True)

    def __str__(self):
        return self.geraet_name


class Ligen(models.Model):
    liga = models.CharField(max_length=50, blank=True, default='', null=True)
    liga_ab = models.DateField(default='1900-01-01')
    liga_bis = models.DateField(default='1900-01-01')

    def __str__(self):
        return self.liga


class Teilnehmer(models.Model):
    GENDER = (
        ('w', 'weiblich'),
        ('m', 'männlich'),
    )
    LIGA_TAG = (
        ('1', '1. Wettkampftag'),
        ('2', '2. Wettkampftag'),
    )
    LIGA = (
        ('A', 'A-Liga'),
        ('B', 'B-Liga'),
        ('C', 'C-Liga'),
        ('D', 'D-Liga'),
        ('E', 'E-Liga'),
        ('F', 'F-Liga'),
    )
    MANNSCHAFT = (
        ('1', '1. Mannschaft'),
        ('2', '2. Mannschaft'),
        ('3', '3. Mannschaft'),
    )
    teilnehmer_name = models.CharField(max_length=30, blank=True, default='', null=True)
    teilnehmer_vorname = models.CharField(max_length=30, blank=True, default='', null=True)
    teilnehmer_geburtsjahr = models.DateField(default='1900-01-01')
    teilnehmer_gender = models.CharField(max_length=1, choices=GENDER, default='w')
    teilnehmer_verein = models.ForeignKey(Vereine, on_delete=models.PROTECT, null=True)
    teilnehmer_anwesend = models.BooleanField(default=True, null=True)
    teilnehmer_liga_tag = models.CharField(max_length=1, choices=LIGA_TAG, default='1')
    teilnehmer_liga = models.CharField(max_length=1, choices=LIGA, default='A')
    teilnehmer_mannschaft = models.CharField(max_length=1, choices=MANNSCHAFT, default='1')
    teilnehmer_ak = models.BooleanField(default=False, null=True)
    teilnehmer_sprung = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_mini = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_reck_stufenbarren = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True,
                                                       default=0)
    teilnehmer_balken = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_barren = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_boden = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)

    def __str__(self):
        return self.teilnehmer_name + ' ' + self.teilnehmer_vorname

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['teilnehmer_name',
                                            'teilnehmer_vorname',
                                            'teilnehmer_geburtsjahr',
                                            'teilnehmer_verein',
                                            'teilnehmer_liga_tag'], name='unique liga_name_vorname_geburtsjahr_verein'),
        ]


class LigaturnenErgebnisse(models.Model):
    ergebnis_teilnehmer = models.ForeignKey(Teilnehmer, on_delete=models.PROTECT, null=True)
    ergebnis_ligatag = models.CharField(max_length=1, default=1, null=True)
    ergebnis_sprung_a = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_sprung_b = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_sprung_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_mini_a = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_mini_b = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_mini_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_reck_a = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_reck_b = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_reck_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_balken_a = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_balken_b = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_balken_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_barren_a = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_barren_b = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_barren_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_boden_a = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_boden_b = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_boden_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_summe = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.ergebnis_teilnehmer)

    def save(self, *args, **kwargs):
        self.ergebnis_sprung_s = self.ergebnis_sprung_a + self.ergebnis_sprung_b
        self.ergebnis_reck_s = self.ergebnis_reck_a + self.ergebnis_reck_b
        self.ergebnis_mini_s = self.ergebnis_mini_a + self.ergebnis_mini_b
        self.ergebnis_balken_s = self.ergebnis_balken_a + self.ergebnis_balken_b
        self.ergebnis_barren_s = self.ergebnis_barren_a + self.ergebnis_barren_b
        self.ergebnis_boden_s = self.ergebnis_boden_a + self.ergebnis_boden_b

        self.ergebnis_summe = self.ergebnis_sprung_s + self.ergebnis_mini_s + self.ergebnis_reck_s + \
                              self.ergebnis_balken_s + self.ergebnis_barren_s + self.ergebnis_boden_s

        super(LigaturnenErgebnisse, self).save(*args, **kwargs)


class LigaturnenErgebnisseZwischenLiga(models.Model):
    GENDER = (
        ('w', 'weiblich'),
        ('m', 'männlich'),
    )
    liga = models.ForeignKey(Ligen, on_delete=models.PROTECT, null=True)
    verein = models.ForeignKey(Vereine, on_delete=models.PROTECT, null=True)
    mannschaft = models.IntegerField(null=True, default=1, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='w')
    ligatag = models.CharField(max_length=1, default=1, null=True)
    ergebnis_summe = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.liga) + " " + str(self.verein) + " " + str(self.mannschaft)


class LigaturnenErgebnisseZwischenLigaGesamt(models.Model):
    GENDER = (
        ('w', 'weiblich'),
        ('m', 'männlich'),
    )
    liga = models.ForeignKey(Ligen, on_delete=models.PROTECT, null=True)
    verein = models.ForeignKey(Vereine, on_delete=models.PROTECT, null=True)
    mannschaft = models.IntegerField(null=True, default=1, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='w')
    ergebnis_summe = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.liga) + " " + str(self.verein) + " " + str(self.mannschaft)

class LigaturnenErgebnisseZwischenEinzel(models.Model):

    GENDER = (
        ('w', 'weiblich'),
        ('m', 'männlich'),
    )

    teilnehmer_name = models.CharField(max_length=30, blank=True, default='', null=True)
    teilnehmer_vorname = models.CharField(max_length=30, blank=True, default='', null=True)
    teilnehmer_geburtsjahr = models.DateField(default='1900-01-01')
    teilnehmer_gender = models.CharField(max_length=1, choices=GENDER, default='w')
    teilnehmer_liga = models.CharField(max_length=1, blank=True, default='', null=True)
    teilnehmer_verein = models.ForeignKey(Vereine, on_delete=models.PROTECT, null=True)
    ergebnis_sprung_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_mini_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_reck_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_balken_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_barren_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_boden_s = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    ergebnis_summe = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.teilnehmer_name) + " " + str(self.teilnehmer_vorname)

    def save(self, *args, **kwargs):
        self.ergebnis_summe = self.ergebnis_sprung_s + self.ergebnis_mini_s + self.ergebnis_reck_s + \
                              self.ergebnis_balken_s + self.ergebnis_barren_s + self.ergebnis_boden_s

        super(LigaturnenErgebnisseZwischenEinzel, self).save(*args, **kwargs)


class LigaTag(models.Model):
    ligatag = models.IntegerField(default=1, blank=True)
    ligajahr = models.CharField(max_length=4, blank=True, default='', null=True)

    def __str__(self):
        return str(self.ligatag)

class Konfiguration(models.Model):
    abstand_urkunde_einzel = models.IntegerField(default=0, null=True, blank=True,)
    abstand_urkunde_mannschaft = models.IntegerField(default=0, null=True, blank=True,)
    liga_jahr = models.CharField(max_length=4, blank=True, default='', null=True)

    def __str__(self):
        return str(self.abstand_urkunde_einzel)