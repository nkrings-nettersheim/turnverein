from django.test import TestCase
from django.db import models
from datetime import date

from ligaturnen.models import Vereine, Geraete, Ligen


class VereineModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Vereine.objects.create(verein_name='Verein1lang',
                               verein_name_kurz='Verein1kurz',
                               verein_strasse='Hauptstr.',
                               verein_plz='53947',
                               verein_ort='Nettersheim',
                               verein_telefon='02486/99999',
                               verein_email='verein@vereine.de')

    def test_verein_name_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_name').verbose_name
        max_length = verein._meta.get_field('verein_name').max_length
        blank = verein._meta.get_field('verein_name').blank
        default = verein._meta.get_field('verein_name').default
        null = verein._meta.get_field('verein_name').null
        self.assertEqual(field_label, 'verein name')
        self.assertEqual(max_length, 75)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)

    def test_verein_name_kurz_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_name_kurz').verbose_name
        max_length = verein._meta.get_field('verein_name_kurz').max_length
        blank = verein._meta.get_field('verein_name_kurz').blank
        default = verein._meta.get_field('verein_name_kurz').default
        null = verein._meta.get_field('verein_name_kurz').null
        self.assertEqual(field_label, 'verein name kurz')
        self.assertEqual(max_length, 20)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)

    def test_verein_strasse_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_strasse').verbose_name
        max_length = verein._meta.get_field('verein_strasse').max_length
        blank = verein._meta.get_field('verein_strasse').blank
        default = verein._meta.get_field('verein_strasse').default
        null = verein._meta.get_field('verein_strasse').null
        self.assertEqual(field_label, 'verein strasse')
        self.assertEqual(max_length, 100)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)

    def test_verein_plz_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_plz').verbose_name
        max_length = verein._meta.get_field('verein_plz').max_length
        blank = verein._meta.get_field('verein_plz').blank
        default = verein._meta.get_field('verein_plz').default
        null = verein._meta.get_field('verein_plz').null
        self.assertEqual(field_label, 'verein plz')
        self.assertEqual(max_length, 5)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)
    
    def test_verein_ort_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_ort').verbose_name
        max_length = verein._meta.get_field('verein_ort').max_length
        blank = verein._meta.get_field('verein_ort').blank
        default = verein._meta.get_field('verein_ort').default
        null = verein._meta.get_field('verein_ort').null
        self.assertEqual(field_label, 'verein ort')
        self.assertEqual(max_length, 100)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)

    def test_verein_telefon_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_telefon').verbose_name
        max_length = verein._meta.get_field('verein_telefon').max_length
        blank = verein._meta.get_field('verein_telefon').blank
        default = verein._meta.get_field('verein_telefon').default
        null = verein._meta.get_field('verein_telefon').null
        self.assertEqual(field_label, 'verein telefon')
        self.assertEqual(max_length, 100)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)
        
    def test_verein_email_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_email').verbose_name
        max_length = verein._meta.get_field('verein_email').max_length
        blank = verein._meta.get_field('verein_email').blank
        self.assertEqual(field_label, 'verein email')
        self.assertEqual(max_length, 254)
        self.assertEqual(blank, True)

    def test_object_name_is_verein_name_kurz(self):
        verein = Vereine.objects.get(id=1)
        expected_object_name = f'{verein.verein_name_kurz}'
        self.assertEqual(str(verein), expected_object_name)


class GeraeteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Geraete.objects.create(geraet_name='Sprung',geraet_db_name='teilnehmern_sprung')

    def test_geraet_name_label(self):
        geraet = Geraete.objects.get(id=1)
        field_label = geraet._meta.get_field('geraet_name').verbose_name
        max_length = geraet._meta.get_field('geraet_name').max_length
        blank = geraet._meta.get_field('geraet_name').blank
        default = geraet._meta.get_field('geraet_name').default
        null = geraet._meta.get_field('geraet_name').null
        self.assertEqual(field_label, 'geraet name')
        self.assertEqual(max_length, 30)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)
        
    def test_geraet_db_name_label(self):
        geraet = Geraete.objects.get(id=1)
        field_label = geraet._meta.get_field('geraet_db_name').verbose_name
        max_length = geraet._meta.get_field('geraet_db_name').max_length
        blank = geraet._meta.get_field('geraet_db_name').blank
        default = geraet._meta.get_field('geraet_db_name').default
        null = geraet._meta.get_field('geraet_db_name').null
        self.assertEqual(field_label, 'geraet db name')
        self.assertEqual(max_length, 30)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)

    def test_object_name_is_geraet_name(self):
        geraet = Geraete.objects.get(id=1)
        expected_object_name = f'{geraet.geraet_name}'
        self.assertEqual(str(geraet), expected_object_name)


class LigenModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Ligen.objects.create(liga='A',liga_ab='2000-01-01', liga_bis='2021-12-31')

    def test_liga_label(self):
        liga = Ligen.objects.get(id=1)
        field_label = liga._meta.get_field('liga').verbose_name
        max_length = liga._meta.get_field('liga').max_length
        blank = liga._meta.get_field('liga').blank
        default = liga._meta.get_field('liga').default
        null = liga._meta.get_field('liga').null
        self.assertEqual(field_label, 'liga')
        self.assertEqual(max_length, 50)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)

    def test_liga_ab_label(self):
        liga = Ligen.objects.get(id=1)
        field_label = liga._meta.get_field('liga_ab').verbose_name
        self.assertIsInstance(liga.liga_ab, date)
        self.assertEqual(field_label, 'liga ab')

    def test_liga_bis_label(self):
        liga = Ligen.objects.get(id=1)
        field_label = liga._meta.get_field('liga_bis').verbose_name
        self.assertIsInstance(liga.liga_ab, date)
        self.assertEqual(field_label, 'liga bis')

    def test_object_name_is_liga(self):
        liga = Ligen.objects.get(id=1)
        expected_object_name = f'{liga.liga}'
        self.assertEqual(str(liga), expected_object_name)