from django.test import TestCase
from datetime import date

from turnfest.models import Vereine, Geraete, Medaille, Meisterschaften

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
        self.assertIsInstance(verein.verein_name, str)

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
        self.assertIsInstance(verein.verein_name_kurz, str)

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
        self.assertIsInstance(verein.verein_strasse, str)

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
        self.assertIsInstance(verein.verein_plz, str)

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
        self.assertIsInstance(verein.verein_ort, str)

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
        self.assertIsInstance(verein.verein_telefon, str)

    def test_verein_email_label(self):
        verein = Vereine.objects.get(id=1)
        field_label = verein._meta.get_field('verein_email').verbose_name
        max_length = verein._meta.get_field('verein_email').max_length
        blank = verein._meta.get_field('verein_email').blank
        self.assertEqual(field_label, 'verein email')
        self.assertEqual(max_length, 254)
        self.assertEqual(blank, True)
        self.assertIsInstance(verein.verein_email, str)

    def test_object_name_is_verein_name_kurz(self):
        verein = Vereine.objects.get(id=1)
        expected_object_name = f'{verein.verein_name_kurz}'
        self.assertEqual(str(verein), expected_object_name)


class GeraeteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Geraete.objects.create(geraet_name='Sprung', geraet_db_name='teilnehmern_sprung')

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
        self.assertIsInstance(geraet.geraet_name, str)

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
        self.assertIsInstance(geraet.geraet_db_name, str)

    def test_object_name_is_geraet_name(self):
        geraet = Geraete.objects.get(id=1)
        expected_object_name = f'{geraet.geraet_name}'
        self.assertEqual(str(geraet), expected_object_name)


class MedailleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Medaille.objects.create(medaille='Gold', punkte_ab=10, punkte_bis=20)

    def test_medaille_label(self):
        medaille = Medaille.objects.get(id=1)
        field_label = medaille._meta.get_field('medaille').verbose_name
        max_length = medaille._meta.get_field('medaille').max_length
        blank = medaille._meta.get_field('medaille').blank
        default = medaille._meta.get_field('medaille').default
        null = medaille._meta.get_field('medaille').null
        self.assertEqual(field_label, 'medaille')
        self.assertEqual(max_length, 30)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)
        self.assertIsInstance(medaille.medaille, str)

    def test_punkte_ab_label(self):
        medaille = Medaille.objects.get(id=1)
        field_label = medaille._meta.get_field('punkte_ab').verbose_name
        blank = medaille._meta.get_field('punkte_ab').blank
        null = medaille._meta.get_field('punkte_ab').null
        self.assertEqual(field_label, 'punkte ab')
        self.assertEqual(blank, True)
        self.assertEqual(null, True)
        self.assertIsInstance(medaille.punkte_ab, int)

    def test_punkte_bis_label(self):
        medaille = Medaille.objects.get(id=1)
        field_label = medaille._meta.get_field('punkte_bis').verbose_name
        blank = medaille._meta.get_field('punkte_bis').blank
        null = medaille._meta.get_field('punkte_bis').null
        self.assertEqual(field_label, 'punkte bis')
        self.assertEqual(blank, True)
        self.assertEqual(null, True)
        self.assertIsInstance(medaille.punkte_bis, int)

    def test_object_name_is_medaille_name(self):
        medaille = Medaille.objects.get(id=1)
        expected_object_name = f'{medaille.medaille}'
        self.assertEqual(str(medaille), expected_object_name)


class MeisterschaftenModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Meisterschaften.objects.create(meisterschaft='Bezirksmeisterin',
                                       meisterschaft_gender='w',
                                       meisterschaft_ab='2010-01-01',
                                       meisterschaft_bis='2015-01-01')

    def test_meisterschaft_label(self):
        meisterschaften = Meisterschaften.objects.get(id=1)
        field_label = meisterschaften._meta.get_field('meisterschaft').verbose_name
        max_length = meisterschaften._meta.get_field('meisterschaft').max_length
        blank = meisterschaften._meta.get_field('meisterschaft').blank
        default = meisterschaften._meta.get_field('meisterschaft').default
        null = meisterschaften._meta.get_field('meisterschaft').null
        self.assertEqual(field_label, 'meisterschaft')
        self.assertEqual(max_length, 30)
        self.assertEqual(blank, True)
        self.assertEqual(default, '')
        self.assertEqual(null, True)
        self.assertIsInstance(meisterschaften.meisterschaft, str)

    def test_meisterschaft_gender_label(self):
        meisterschaften = Meisterschaften.objects.get(id=1)
        field_label = meisterschaften._meta.get_field('meisterschaft_gender').verbose_name
        max_length = meisterschaften._meta.get_field('meisterschaft_gender').max_length
        default = meisterschaften._meta.get_field('meisterschaft_gender').default
        self.assertEqual(field_label, 'meisterschaft gender')
        self.assertEqual(max_length, 1)
        self.assertEqual(default, '1')
        self.assertIsInstance(meisterschaften.meisterschaft_gender, str)


    def test_meisterschaft_ab_label(self):
        meisterschaften = Meisterschaften.objects.get(id=1)
        field_label = meisterschaften._meta.get_field('meisterschaft_ab').verbose_name
        default = meisterschaften._meta.get_field('meisterschaft_ab').default
        self.assertEqual(field_label, 'meisterschaft ab')
        self.assertEqual(default, '1900-01-01')
        self.assertIsInstance(meisterschaften.meisterschaft_ab, date)

    def test_meisterschaft_bis_label(self):
        meisterschaften = Meisterschaften.objects.get(id=1)
        field_label = meisterschaften._meta.get_field('meisterschaft_bis').verbose_name
        default = meisterschaften._meta.get_field('meisterschaft_bis').default
        self.assertEqual(field_label, 'meisterschaft bis')
        self.assertEqual(default, '1900-01-01')
        self.assertIsInstance(meisterschaften.meisterschaft_bis, date)

    def test_object_name_is_meisterschaft(self):
        meisterschaften = Meisterschaften.objects.get(id=1)
        expected_object_name = f'{meisterschaften.meisterschaft} {meisterschaften.get_meisterschaft_gender_display}'
        self.assertEqual(str(meisterschaften), expected_object_name)


