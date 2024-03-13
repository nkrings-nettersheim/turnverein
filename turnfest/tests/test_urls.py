from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User, Permission
from turnfest.views import *
from turnfest.models import Vereine


class HomepageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')

        content_type = ContentType.objects.get_for_model(
            Vereine)  # Hier wird die Berechtigung für das User-Modell erstellt

        permissions = [
            {'codename': 'view_bezirksturnfestergebnisse', 'name': 'Can view bezirksturnfestergebnisse'},
            {'codename': 'change_bezirksturnfestergebnisse', 'name': 'Can change bezirksturnfestergebnisse'},
            {'codename': 'add_bezirksturnfestergebnisse', 'name': 'Can add bezirksturnfestergebnisse'},
            {'codename': 'delete_bezirksturnfestergebnisse', 'name': 'Can delete bezirksturnfestergebnisse'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 301) #301 Moved Permanently

    def test_homepage_available_by_name(self):
        response = self.client.get(reverse('turnfest:index'))
        self.assertEqual(response.status_code, 302) #302 Found (Moved Temporarily)

    def test_impressum_exists_at_correct_location(self):
        response = self.client.get("/turnfest/impressum/")
        self.assertEqual(response.status_code, 200)

    def test_impressum_available_by_name(self):
        response = self.client.get(reverse('turnfest:impressum'))
        self.assertEqual(response.status_code, 200)

    def test_datenschutz_exists_at_correct_location(self):
        response = self.client.get("/turnfest/datenschutz/")
        self.assertEqual(response.status_code, 200)

    def test_datenschutz_available_by_name(self):
        response = self.client.get(reverse('turnfest:datenschutz'))
        self.assertEqual(response.status_code, 200)

    def test_bezirksturnfest_ansicht_ohne_anmeldung(self):
        # Rufe die geschützte Ansicht auf, ohne angemeldet zu sein
        #url = reverse('geschuetzte_ansicht')  # Annahme, dass die URL so benannt ist
        response = self.client.get("/turnfest/bezirksturnfest/")

        # Überprüfe, ob der Benutzer umgeleitet wurde (Statuscode 302 für Umleitung)
        self.assertEqual(response.status_code, 302)

        # Überprüfe, ob die Umleitung zur Anmeldeseite erfolgte
        #self.assertRedirects(response, reverse('login'))
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/bezirksturnfest/')

    def test_bezirksturnfest_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/bezirksturnfest/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'turnfest/bezirksturnfest.html')

    def test_bezirksturnfest_available_by_name(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('turnfest:bezirksturnfest'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/bezirksturnfest.html')

class VereineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")

        content_type = ContentType.objects.get_for_model(Vereine)

        permissions = [
            {'codename': 'view_vereine', 'name': 'Can view vereine'},
            {'codename': 'change_vereine', 'name': 'Can change vereine'},
            {'codename': 'add_vereine', 'name': 'Can add vereine'},
            {'codename': 'delete_vereine', 'name': 'Can delete vereine'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_vereine_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/turnfest/vereine_create/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/vereine_create/')

        response = self.client.get("/turnfest/vereine_list/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/vereine_list/')

        response = self.client.get("/turnfest/vereine_detail/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/vereine_detail/1/')

        response = self.client.get("/turnfest/vereine_edit/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/vereine_edit/1/')

        response = self.client.get("/turnfest/vereine_delete/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/vereine_delete/1/')

        response = self.client.get("/turnfest/vereine_upload/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/vereine_upload/')

        response = self.client.get("/turnfest/report_vereine/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/report_vereine/')

    def test_vereine_create_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/vereine_create/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'turnfest/vereine_create.html')

        response = self.client.get(reverse('turnfest:vereine_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_create.html')

    def test_vereine_list_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/vereine_list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_list.html')

        response = self.client.get(reverse('turnfest:vereine_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_list.html')

    def test_vereine_detail_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/vereine_detail/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_detail.html')

        response = self.client.get(reverse('turnfest:vereine_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_detail.html')

    def test_vereine_edit_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/vereine_edit/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_edit.html')

        response = self.client.get(reverse('turnfest:vereine_edit', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_edit.html')

    def test_vereine_delete_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/vereine_delete/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_delete.html')

        response = self.client.get(reverse('turnfest:vereine_delete', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_delete.html')

    def test_vereine_upload_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/vereine_upload/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_upload.html')

        response = self.client.get(reverse('turnfest:vereine_upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/vereine_upload.html')

class TeilnehmerTests(TestCase):

    @classmethod
    def setUp(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Teilnehmer.objects.create(teilnehmer_name='TestName',
                                  teilnehmer_vorname='TestVorname',
                                  teilnehmer_verein_id=1
                                  )

        content_type = ContentType.objects.get_for_model(Teilnehmer)

        permissions = [
            {'codename': 'view_teilnehmer', 'name': 'Can view teilnehmer'},
            {'codename': 'change_teilnehmer', 'name': 'Can change teilnehmer'},
            {'codename': 'add_teilnehmer', 'name': 'Can add teilnehmer'},
            {'codename': 'delete_teilnehmer', 'name': 'Can delete teilnehmer'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_teilnehmer_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/turnfest/teilnehmer_create/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/teilnehmer_create/')

        response = self.client.get("/turnfest/teilnehmer_list/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/teilnehmer_list/')

        response = self.client.get("/turnfest/teilnehmer_detail/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/teilnehmer_detail/1/')

        response = self.client.get("/turnfest/teilnehmer_edit/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/teilnehmer_edit/1/')

        response = self.client.get("/turnfest/teilnehmer_delete/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/teilnehmer_delete/1/')

        response = self.client.get("/turnfest/teilnehmer_upload/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/teilnehmer_upload/')

    def test_teilnehmer_create_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/teilnehmer_create/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_create.html')

        response = self.client.get(reverse('turnfest:teilnehmer_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_create.html')

    def test_teilnehmer_list_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/teilnehmer_list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_list.html')

        response = self.client.get(reverse('turnfest:teilnehmer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_list.html')

    def test_teilnehmer_detail_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/teilnehmer_detail/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_detail.html')

        response = self.client.get(reverse('turnfest:teilnehmer_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_detail.html')

    def test_teilnehmer_edit_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/teilnehmer_edit/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_edit.html')

        response = self.client.get(reverse('turnfest:teilnehmer_edit', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_edit.html')

    def test_teilnehmer_delete_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/teilnehmer_delete/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_delete.html')

        response = self.client.get(reverse('turnfest:teilnehmer_delete', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_delete.html')

    def test_teilnehmer_upload_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/teilnehmer_upload/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_upload.html')

        response = self.client.get(reverse('turnfest:teilnehmer_upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/teilnehmer_upload.html')

class ErgebnisseTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Teilnehmer.objects.create(teilnehmer_name="Muster")
        Geraete.objects.create(geraet_name="Sprung")
        BezirksturnfestErgebnisse.objects.create(ergebnis_teilnehmer_id=1)
        
        content_type = ContentType.objects.get_for_model(BezirksturnfestErgebnisse)

        permissions = [
            {'codename': 'view_bezirksturnfestergebnisse', 'name': 'Can view bezirksturnfestergebnisse'},
            {'codename': 'change_bezirksturnfestergebnisse', 'name': 'Can change bezirksturnfestergebnisse'},
            {'codename': 'add_bezirksturnfestergebnisse', 'name': 'Can add bezirksturnfestergebnisse'},
            {'codename': 'delete_bezirksturnfestergebnisse', 'name': 'Can delete bezirksturnfestergebnisse'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_bezirksturnfestergebnisse_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/turnfest/ergebnis_erfassen_suche/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/ergebnis_erfassen_suche/')

        response = self.client.get("/turnfest/add/ergebnis/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/add/ergebnis/')

        response = self.client.get("/turnfest/edit/ergebnis/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/edit/ergebnis/1/')

        response = self.client.get("/turnfest/ergebnisse_list/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/ergebnisse_list/')

    def test_bezirksturnfestergebnisse_list_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/ergebnisse_list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnisse_list.html')

        response = self.client.get(reverse('turnfest:ergebnisse_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnisse_list.html')

    def test_bezirksturnfestergebnisse_suche_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['geraet'] = 1
        session['teilnehmer'] = 1
        session.save()

        response = self.client.get("/turnfest/ergebnis_erfassen_suche/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnis_erfassen_suche.html')

        response = self.client.get(reverse('turnfest:ergebnis_erfassen_suche'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnis_erfassen_suche.html')

    def test_bezirksturnfestergebnisse_add_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['geraet'] = 1
        session['startnummer'] = 1
        session.save()

        response = self.client.get("/turnfest/add/ergebnis/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnis_erfassen.html')

        response = self.client.get(reverse('turnfest:add_ergebnis'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnis_erfassen.html')

    def test_edit_ergebnis_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['geraet'] = 1
        session['startnummer'] = 1
        session.save()

        response = self.client.get("/turnfest/edit/ergebnis/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnis_erfassen.html')

        response = self.client.get(reverse('turnfest:edit_ergebnis', args=['1']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'turnfest/ergebnis_erfassen.html')

class AuswertungenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Teilnehmer.objects.create(teilnehmer_name="Muster")
        Geraete.objects.create(geraet_name="Sprung")
        BezirksturnfestErgebnisse.objects.create(ergebnis_teilnehmer_id=1)
        Konfiguration.objects.create(jahr='2024', bezirksturnfest='81. Bezirksturnfest')

        content_type = ContentType.objects.get_for_model(BezirksturnfestErgebnisse)

        permissions = [
            {'codename': 'view_bezirksturnfestergebnisse', 'name': 'Can view bezirksturnfestergebnisse'},
            {'codename': 'change_bezirksturnfestergebnisse', 'name': 'Can change bezirksturnfestergebnisse'},
            {'codename': 'add_bezirksturnfestergebnisse', 'name': 'Can add bezirksturnfestergebnisse'},
            {'codename': 'delete_bezirksturnfestergebnisse', 'name': 'Can delete bezirksturnfestergebnisse'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)
        
        content_type = ContentType.objects.get_for_model(Teilnehmer)

        permissions = [
            {'codename': 'view_teilnehmer', 'name': 'Can view teilnehmer'},
            {'codename': 'change_teilnehmer', 'name': 'Can change teilnehmer'},
            {'codename': 'add_teilnehmer', 'name': 'Can add teilnehmer'},
            {'codename': 'delete_teilnehmer', 'name': 'Can delete teilnehmer'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)
            
    def test_auswertung_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/turnfest/geraetelisten/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/geraetelisten/')

        response = self.client.get("/turnfest/auswertung/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/auswertung/')

        response = self.client.get("/turnfest/urkunden/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/urkunden/')

        response = self.client.get("/turnfest/auswertung_vereine/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/turnfest/auswertung_vereine/')

    def test_geraetelisten_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/geraetelisten/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('turnfest:geraetelisten'))
        self.assertEqual(response.status_code, 200)

    def test_auswertung_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/auswertung/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('turnfest:auswertung'))
        self.assertEqual(response.status_code, 200)
        
    def test_urkunden_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/urkunden/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('turnfest:urkunden'))
        self.assertEqual(response.status_code, 200)
        
    def test_auswertung_vereine_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/auswertung_vereine/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('turnfest:auswertung_vereine'))
        self.assertEqual(response.status_code, 200)

class DeleteTables_Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Teilnehmer.objects.create(teilnehmer_name="Muster")
        Geraete.objects.create(geraet_name="Sprung")
        BezirksturnfestErgebnisse.objects.create(ergebnis_teilnehmer_id=1)

        content_type = ContentType.objects.get_for_model(BezirksturnfestErgebnisse)

        permissions = [
            {'codename': 'view_bezirksturnfestergebnisse', 'name': 'Can view bezirksturnfestergebnisse'},
            {'codename': 'change_bezirksturnfestergebnisse', 'name': 'Can change bezirksturnfestergebnisse'},
            {'codename': 'add_bezirksturnfestergebnisse', 'name': 'Can add bezirksturnfestergebnisse'},
            {'codename': 'delete_bezirksturnfestergebnisse', 'name': 'Can delete bezirksturnfestergebnisse'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_delete_tables_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/turnfest/delete_tables/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('turnfest:delete_tables'))
        self.assertEqual(response.status_code, 200)