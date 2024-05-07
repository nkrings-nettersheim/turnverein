from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models import CharField
import datetime


class Vereine(models.Model):
    verein_name = models.CharField(max_length=75, blank=True, default='', null=True)
    verein_name_kurz = models.CharField(max_length=20, blank=True, default='', null=True)
    verein_strasse = models.CharField(max_length=100, blank=True, default='', null=True)
    verein_plz = models.CharField(max_length=5, blank=True, default='', null=True)
    verein_ort = models.CharField(max_length=100, blank=True, default='', null=True)
    verein_telefon = models.CharField(max_length=100, blank=True, default='', null=True)
    verein_email = models.EmailField(max_length=254, blank=True)
    verein_aktiv = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.verein_name_kurz


class Geraete(models.Model):
    geraet_name = models.CharField(max_length=30, blank=True, default='', null=True)
    geraet_db_name = models.CharField(max_length=30, blank=True, default='', null=True)

    def __str__(self):
        return self.geraet_name


class Medaille(models.Model):
    medaille = models.CharField(max_length=30, blank=True, default='', null=True)
    punkte_ab = models.IntegerField(blank=True, null=True)
    punkte_bis = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.medaille


class Meisterschaften(models.Model):
    GENDER = (
        ('w', 'weiblich'),
        ('m', 'männlich'),
    )
    meisterschaft = models.CharField(max_length=30, blank=True, default='', null=True)
    meisterschaft_gender = models.CharField(max_length=1, choices=GENDER, default='1')
    meisterschaft_ab = models.DateField(default='1900-01-01')
    meisterschaft_bis = models.DateField(default='1900-01-01')

    def __str__(self):
        return self.meisterschaft + " " + self.meisterschaft_gender


#Bei der nächsten Bereinigung kann dieses Model komplett entfernt werden
class Bezirksturnfest(models.Model):
    bezirksturnfest = models.CharField(max_length=50, blank=True, default='', null=True)
    austragungsort = models.CharField(max_length=30, blank=True, default='', null=True)
    wettkampftag = models.DateField()

    def __str__(self):
        return self.bezirksturnfest


class Riegen(models.Model):
    riege = models.CharField(max_length=50, blank=True, default='', null=True)
    riege_ab = models.DateField(default='1900-01-01')
    riege_bis = models.DateField(default='1900-01-01')

    def __str__(self):
        return self.riege


class Teilnehmer(models.Model):
    GENDER = (
        ('w', 'weiblich'),
        ('m', 'männlich'),
    )
    teilnehmer_name = models.CharField(max_length=30, blank=True, default='', null=True)
    teilnehmer_vorname = models.CharField(max_length=30, blank=True, default='', null=True)
    teilnehmer_geburtsjahr = models.DateField(default='1900-01-01')
    teilnehmer_gender = models.CharField(max_length=1, choices=GENDER, default='w')
    teilnehmer_verein = models.ForeignKey(Vereine, on_delete=models.PROTECT, null=True)
    teilnehmer_anwesend = models.BooleanField(default=True, null=True)
    teilnehmer_sprung = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_mini = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_reck_stufenbarren = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_balken = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_barren = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)
    teilnehmer_boden = models.IntegerField(validators=[MaxValueValidator(10)], null=True, blank=True, default=0)

    def __str__(self):
        return self.teilnehmer_name + ' ' + self.teilnehmer_vorname

    def formatiertes_datum(self):
        return self.teilnehmer_geburtsjahr.strftime('%Y')

    @property
    def full_name(self):
        "Returns the person's full name."
        return f"{self.teilnehmer_name} {self.teilnehmer_vorname}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['teilnehmer_name',
                                            'teilnehmer_vorname',
                                            'teilnehmer_geburtsjahr',
                                            'teilnehmer_verein'], name='unique name_vorname_geburtsjahr_verein'),
        ]


class BezirksturnfestErgebnisse(models.Model):
    ergebnis_teilnehmer = models.ForeignKey(Teilnehmer, on_delete=models.PROTECT, null=True)
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
    ergebnis_summe = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    ergebnis_ranking = models.IntegerField(null=True, blank=True, default=0)

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

        super(BezirksturnfestErgebnisse, self).save(*args, **kwargs)


class Konfiguration(models.Model):
    abstand_urkunde_einzel = models.IntegerField(default=0, null=True, blank=True,)
    abstand_urkunde_mannschaft = models.IntegerField(default=0, null=True, blank=True,)
    jahr = models.CharField(max_length=4, blank=True, default='', null=True)
    bezirksturnfest = models.CharField(max_length=255, blank=True, default='', null=True)
    kosten_teilnehmer = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    bezirksturnfest_aktiv = models.BooleanField(default=True, null=True)

    def __str__(self):
        return str(self.abstand_urkunde_einzel)