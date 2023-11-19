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


class Wettkampfteilnahme(models.Model):
    wktn_teilnehmer = models.ForeignKey(Teilnehmer, on_delete=models.PROTECT, null=True)
    wktn_bezirksturnfest = models.ForeignKey(Bezirksturnfest, on_delete=models.PROTECT, null=True)
    wktn_anwesend = models.BooleanField(default=False, null=True)
    wktn_sprung = models.BooleanField(default=False, null=True)
    wktn_mini = models.BooleanField(default=False, null=True)
    wktn_reck = models.BooleanField(default=False, null=True)
    wktn_balken = models.BooleanField(default=False, null=True)
    wktn_barren = models.BooleanField(default=False, null=True)
    wktn_boden = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.wktn_teilnehmer

