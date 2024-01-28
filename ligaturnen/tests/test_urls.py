from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User, Permission
from ligaturnen.views import *
from ligaturnen.models import Vereine

class HomepageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')

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

    def test_ligawettkampf_ansicht_ohne_anmeldung(self):
        # Rufe die geschützte Ansicht auf, ohne angemeldet zu sein
        #url = reverse('geschuetzte_ansicht')  # Annahme, dass die URL so benannt ist
        response = self.client.get("/ligaturnen/ligawettkampf/")

        # Überprüfe, ob der Benutzer umgeleitet wurde (Statuscode 302 für Umleitung)
        self.assertEqual(response.status_code, 302)

        # Überprüfe, ob die Umleitung zur Anmeldeseite erfolgte
        #self.assertRedirects(response, reverse('login'))
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ligawettkampf/')

    def test_ligawettkampf_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ligawettkampf/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'ligaturnen/ligawettkampf.html')

    def test_ligawettkampf_available_by_name(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(reverse('ligaturnen:ligawettkampf'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligawettkampf.html')

class VereineTests(TestCase):
    @classmethod
    def setUp(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name = "Verein1")
        Ligen.objects.create(liga = "A")
        LigaTag.objects.create(ligatag = "1")

        # Erstelle eine Berechtigung (Permission)
        content_type = ContentType.objects.get_for_model(Vereine)  # Hier wird die Berechtigung für das User-Modell erstellt

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
        response = self.client.get("/ligaturnen/vereine_create/")
        # Überprüfe, ob der Benutzer umgeleitet wurde (Statuscode 302 für Umleitung)
        self.assertEqual(response.status_code, 302)
        # Überprüfe, ob die Umleitung zur Anmeldeseite erfolgte
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/vereine_create/')

        response = self.client.get("/ligaturnen/vereine_list/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/vereine_list/')

        response = self.client.get("/ligaturnen/vereine_detail/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/vereine_detail/1/')

        response = self.client.get("/ligaturnen/vereine_edit/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/vereine_edit/1/')

        response = self.client.get("/ligaturnen/vereine_delete/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/vereine_delete/1/')

        response = self.client.get("/ligaturnen/vereine_upload/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/vereine_upload/')

    def test_vereine_create_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/vereine_create/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'ligaturnen/vereine_create.html')

        response = self.client.get(reverse('ligaturnen:vereine_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_create.html')

    def test_vereine_list_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/vereine_list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_list.html')

        response = self.client.get(reverse('ligaturnen:vereine_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_list.html')

    def test_vereine_detail_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/vereine_detail/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_detail.html')

        response = self.client.get(reverse('ligaturnen:vereine_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_detail.html')

    def test_vereine_edit_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/vereine_edit/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_edit.html')

        response = self.client.get(reverse('ligaturnen:vereine_edit', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_edit.html')

    def test_vereine_delete_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/vereine_delete/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_delete.html')

        response = self.client.get(reverse('ligaturnen:vereine_delete', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_delete.html')

    def test_vereine_upload_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/vereine_upload/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_upload.html')

        response = self.client.get(reverse('ligaturnen:vereine_upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/vereine_upload.html')

class LigenTests(TestCase):

    @classmethod
    def setUp(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Ligen.objects.create(liga="A")
        LigaTag.objects.create(ligatag="1")

        # Erstelle eine Berechtigung (Permission)
        content_type = ContentType.objects.get_for_model(Ligen)  # Hier wird die Berechtigung für das User-Modell erstellt

        permissions = [
            {'codename': 'view_ligen', 'name': 'Can view ligen'},
            {'codename': 'change_ligen', 'name': 'Can change ligen'},
            {'codename': 'add_ligen', 'name': 'Can add ligen'},
            {'codename': 'delete_ligen', 'name': 'Can delete ligen'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_ligen_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/ligaturnen/ligen_create/")
        # Überprüfe, ob der Benutzer umgeleitet wurde (Statuscode 302 für Umleitung)
        self.assertEqual(response.status_code, 302)
        # Überprüfe, ob die Umleitung zur Anmeldeseite erfolgte
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ligen_create/')

        response = self.client.get("/ligaturnen/ligen_list/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ligen_list/')

        response = self.client.get("/ligaturnen/ligen_detail/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ligen_detail/1/')

        response = self.client.get("/ligaturnen/ligen_edit/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ligen_edit/1/')

        response = self.client.get("/ligaturnen/ligen_delete/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ligen_delete/1/')

    def test_ligen_create_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ligen_create/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'ligaturnen/ligen_create.html')

        response = self.client.get(reverse('ligaturnen:ligen_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_create.html')

    def test_ligen_list_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ligen_list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_list.html')

        response = self.client.get(reverse('ligaturnen:ligen_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_list.html')

    def test_ligen_detail_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ligen_detail/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_detail.html')

        response = self.client.get(reverse('ligaturnen:ligen_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_detail.html')

    def test_ligen_edit_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ligen_edit/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_edit.html')

        response = self.client.get(reverse('ligaturnen:ligen_edit', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_edit.html')

    def test_ligen_delete_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ligen_delete/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_delete.html')

        response = self.client.get(reverse('ligaturnen:ligen_delete', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligen_delete.html')

class TeilnehmerTests(TestCase):

    @classmethod
    def setUp(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Ligen.objects.create(liga="A")
        LigaTag.objects.create(ligatag="1")
        Teilnehmer.objects.create(teilnehmer_name = 'TestName',
                                  teilnehmer_vorname = 'TestVorname',
                                  teilnehmer_verein_id = 1,
                                  teilnehmer_liga_tag = '1',
                                  teilnehmer_liga = 'A' )

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
        response = self.client.get("/ligaturnen/teilnehmer_create/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/teilnehmer_create/')

        response = self.client.get("/ligaturnen/teilnehmer_list/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/teilnehmer_list/')

        response = self.client.get("/ligaturnen/teilnehmer_detail/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/teilnehmer_detail/1/')

        response = self.client.get("/ligaturnen/teilnehmer_edit/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/teilnehmer_edit/1/')

        response = self.client.get("/ligaturnen/teilnehmer_delete/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/teilnehmer_delete/1/')

        response = self.client.get("/ligaturnen/teilnehmer_upload/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/teilnehmer_upload/')
        
    def test_teilnehmer_create_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/teilnehmer_create/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_create.html')

        response = self.client.get(reverse('ligaturnen:teilnehmer_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_create.html')

    def test_teilnehmer_list_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/teilnehmer_list/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_list.html')

        response = self.client.get(reverse('ligaturnen:teilnehmer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_list.html')

    def test_teilnehmer_detail_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/teilnehmer_detail/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_detail.html')

        response = self.client.get(reverse('ligaturnen:teilnehmer_detail', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_detail.html')

    def test_teilnehmer_edit_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/teilnehmer_edit/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_edit.html')

        response = self.client.get(reverse('ligaturnen:teilnehmer_edit', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_edit.html')

    def test_teilnehmer_delete_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/teilnehmer_delete/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_delete.html')

        response = self.client.get(reverse('ligaturnen:teilnehmer_delete', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_delete.html')

    def test_teilnehmer_upload_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/teilnehmer_upload/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_upload.html')

        response = self.client.get(reverse('ligaturnen:teilnehmer_upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/teilnehmer_upload.html')

class MixAreaTests(TestCase):

    @classmethod
    def setUp(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Ligen.objects.create(liga="A")
        LigaTag.objects.create(ligatag="1")

        content_type = ContentType.objects.get_for_model(LigaTag)

        permissions = [
            {'codename': 'view_ligatag', 'name': 'Can view ligatag'},
            {'codename': 'change_ligatag', 'name': 'Can change ligatag'},
            {'codename': 'add_ligatag', 'name': 'Can add ligatag'},
            {'codename': 'delete_ligatag', 'name': 'Can delete ligatag'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

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

    def test_download_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/download/?file_name=Teilnehmer_Ligaturnen.xlsx")
        self.assertEqual(response.status_code, 200)

        #response = self.client.get(reverse('ligaturnen:download' + "?file_name=Teilnehmer_Ligaturnen.xlsx"))
        #self.assertEqual(response.status_code, 200)

    def test_geraetelisten_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/geraetelisten/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ligaturnen:geraetelisten'))
        self.assertEqual(response.status_code, 200)

    def test_tables_delete_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/tables_delete/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'ligaturnen/tables_delete.html')

    def test_ligatag_edit_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ligatag_edit/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligatag_edit.html')

        response = self.client.get(reverse('ligaturnen:ligatag_edit', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ligatag_edit.html')



class ErgebnisseTests(TestCase):

    @classmethod
    def setUp(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Ligen.objects.create(liga="A")
        LigaTag.objects.create(ligatag="1")
        Geraete.objects.create(geraet_name="Sprung")
        Geraete.objects.create(geraet_name="Reck")
        Teilnehmer.objects.create(teilnehmer_name="MusterName", teilnehmer_vorname="MusterVorname")
        LigaturnenErgebnisse.objects.create(ergebnis_teilnehmer_id=1)

        # Erstelle eine Berechtigung (Permission)
        content_type = ContentType.objects.get_for_model(LigaturnenErgebnisse)  # Hier wird die Berechtigung für das User-Modell erstellt

        permissions = [
            {'codename': 'view_ligaturnenergebnisse', 'name': 'Can view ligaturnenergebnisse'},
            {'codename': 'change_ligaturnenergebnisse', 'name': 'Can change ligaturnenergebnisse'},
            {'codename': 'add_ligaturnenergebnisse', 'name': 'Can add ligaturnenergebnisse'},
            {'codename': 'delete_ligaturnenergebnisse', 'name': 'Can delete ligaturnenergebnisse'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_ergebnis_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/ligaturnen/ergebnis_erfassen_suche/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ergebnis_erfassen_suche/')

        response = self.client.get("/ligaturnen/add/ergebnis/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/add/ergebnis/')

        response = self.client.get("/ligaturnen/edit/ergebnis/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/edit/ergebnis/1/')

        response = self.client.get("/ligaturnen/ergebnisse_list/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ergebnisse_list/')

    def test_ergebnis_suche_exists_at_correct_location(self):
        # Meldung mit dem Testbenutzer an
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['geraet'] = 1
        session['teilnehmer'] = 1
        session.save()

        response = self.client.get("/ligaturnen/ergebnis_erfassen_suche/")
        self.assertEqual(response.status_code, 200)
        # Überprüfe, ob der richtige Template-Name verwendet wurde
        self.assertTemplateUsed(response, 'ligaturnen/ergebnis_erfassen_suche.html')

        response = self.client.get(reverse('ligaturnen:ergebnis_erfassen_suche'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ergebnis_erfassen_suche.html')

    def test_add_ergebnis_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['geraet'] = 1
        session['startnummer'] = 1
        session.save()

        response = self.client.get("/ligaturnen/add/ergebnis/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ergebnis_erfassen.html')

        response = self.client.get(reverse('ligaturnen:add_ergebnis'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ergebnis_erfassen.html')

    def test_edit_ergebnis_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['geraet'] = 1
        session['startnummer'] = 1
        session.save()

        response = self.client.get("/ligaturnen/edit/ergebnis/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ergebnis_erfassen.html')

        response = self.client.get(reverse('ligaturnen:edit_ergebnis', args=['1']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ligaturnen/ergebnis_erfassen.html')

    def test_ergebnisse_list_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/ergebnisse_list/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ligaturnen:ergebnisse_list'))
        self.assertEqual(response.status_code, 200)

class AuswertungenTests(TestCase):

    @classmethod
    def setUp(cls):
        # Erstelle einen Testbenutzer
        cls.test_user = User.objects.create_user(username='testuser', password='testpassword')
        Vereine.objects.create(verein_name="Verein1")
        Ligen.objects.create(liga="A")
        LigaTag.objects.create(ligatag="1")
        Konfiguration.objects.create(abstand_urkunde_einzel=0, abstand_urkunde_mannschaft=0, liga_jahr='2024')

        content_type = ContentType.objects.get_for_model(LigaturnenErgebnisse)  # Hier wird die Berechtigung für das User-Modell erstellt

        permissions = [
            {'codename': 'view_ligaturnenergebnisse', 'name': 'Can view ligaturnenergebnisse'},
            {'codename': 'change_ligaturnenergebnisse', 'name': 'Can change ligaturnenergebnisse'},
            {'codename': 'add_ligaturnenergebnisse', 'name': 'Can add ligaturnenergebnisse'},
            {'codename': 'delete_ligaturnenergebnisse', 'name': 'Can delete ligaturnenergebnisse'},
        ]

        for permission_data in permissions:
            permission, created = Permission.objects.get_or_create(
                codename=permission_data['codename'],
                content_type=content_type,
                defaults={'name': permission_data['name']},
            )

            cls.test_user.user_permissions.add(permission)

    def test_auswertung_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/ligaturnen/auswertungeinzel/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/auswertungeinzel/')

        response = self.client.get("/ligaturnen/urkundeeinzel/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/urkundeeinzel/')

        response = self.client.get("/ligaturnen/auswertungmannschaft/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/auswertungmannschaft/')

        response = self.client.get("/ligaturnen/urkundemannschaft/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/urkundemannschaft/')

        response = self.client.get("/ligaturnen/auswertungvereine/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/auswertungvereine/')

    def test_auswertungeinzel_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/auswertungeinzel/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ligaturnen:auswertungeinzel'))
        self.assertEqual(response.status_code, 200)

    def test_urkundeeinzel_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/urkundeeinzel/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ligaturnen:urkundeeinzel'))
        self.assertEqual(response.status_code, 200)

    def test_auswertungmannschaft_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/auswertungmannschaft/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ligaturnen:auswertungmannschaft'))
        self.assertEqual(response.status_code, 200)

    def test_urkundemannschaft_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/urkundemannschaft/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ligaturnen:urkundemannschaft'))
        self.assertEqual(response.status_code, 200)

    def test_auswertungvereine_exists_at_correct_location(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get("/ligaturnen/auswertungvereine/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('ligaturnen:auswertungvereine'))
        self.assertEqual(response.status_code, 200)


    def test_mix_area_xyz_ansicht_ohne_anmeldung(self):
        response = self.client.get("/ligaturnen/download/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/download/')

        response = self.client.get("/ligaturnen/geraetelisten/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/geraetelisten/')

        response = self.client.get("/ligaturnen/tables_delete/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/tables_delete/')

        response = self.client.get("/ligaturnen/ligatag_edit/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/ligaturnen/ligatag_edit/1/')
