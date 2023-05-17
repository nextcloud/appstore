from django.contrib.auth import get_user_model
from django.test import TestCase

from nextcloudappstore.core.models import App, AppRelease


class AppSearchTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test", email="test@test.com")
        self.app1 = App.objects.create(pk="news", owner=self.user)
        self.app1.set_current_language("en")
        self.app1.name = "News"
        self.app1.description = "RSS feed reader"
        self.app1.set_current_language("fi")
        self.app1.name = "Uutiset"
        self.app1.description = "RSS-syötelukija"
        self.app1.save()
        AppRelease.objects.create(app=self.app1, version="5.3", platform_version_spec=">=9.1.1")

        self.app2 = App.objects.create(pk="notes", owner=self.user)
        self.app2.set_current_language("en")
        self.app2.name = "Notes"
        self.app2.description = "Notes application"
        self.app2.set_current_language("fi")
        self.app2.name = "Muistiinpanot"
        self.app2.description = "Muistiinpanosovellus"
        self.app2.save()
        AppRelease.objects.create(app=self.app2, version="6.4.2", platform_version_spec=">=9.1.1")

        self.app3 = App.objects.create(pk="calendar", owner=self.user)
        self.app3.set_current_language("en")
        self.app3.name = "Calendar"
        self.app3.description = "Calendar application"
        self.app3.set_current_language("fi")
        self.app3.name = "Kalenteri"
        self.app3.description = "Kalenterisovellus"
        self.app3.save()
        AppRelease.objects.create(app=self.app3, version="9.6.3", platform_version_spec=">=9.1.1")

        self.app4 = App.objects.create(pk="chat", owner=self.user)
        self.app4.set_current_language("en")
        self.app4.name = "Chat"
        self.app4.description = "Chat client"
        self.app4.save()
        AppRelease.objects.create(app=self.app4, version="0.6", platform_version_spec=">=9.1.1")

    def tearDown(self):
        self.app1.delete()
        self.app2.delete()
        self.app3.delete()
        self.app4.delete()
        self.user.delete()

    def test_basic_search(self):
        res = App.objects.search(["app"], "en").all()
        res_fi = App.objects.search(["sovellus"], "fi").all()
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res_fi), 2)

    def test_fallback(self):
        # no translation
        res_chat = App.objects.search(["chat"], "fi").all()
        res_note = App.objects.search(["note"], "de").all()

        # search term in fallback lang, though search in translations
        res_app = App.objects.search(["app"], "fi").all()
        res_cal = App.objects.search(["cal"], "fi").all()

        self.assertEqual(len(res_chat), 1)
        self.assertEqual(len(res_note), 1)
        self.assertEqual(len(res_app), 2)
        self.assertEqual(len(res_cal), 1)
        self.assertEqual(res_chat.get(id="chat").name, "Chat")
        self.assertEqual(res_note.get(id="notes").name, "Notes")
        self.assertEqual(res_app.get(id="calendar").name, "Kalenteri")
        self.assertEqual(res_cal.get(id="calendar").name, "Kalenteri")

    def test_reverse_fallback(self):
        # search term does not exist anywhere
        res_chat = App.objects.search(["chatti"], "en").all()

        res_app = App.objects.search(["sovellus"], "en").all()
        res_cal = App.objects.search(["cal"], "en").all()

        self.assertEqual(len(res_chat), 0)
        self.assertEqual(len(res_app), 2)
        self.assertEqual(len(res_cal), 1)
        self.assertEqual(res_app.get(id="calendar").name, "Calendar")
        self.assertEqual(res_cal.get(id="calendar").name, "Calendar")

    def test_same_word(self):
        res = App.objects.search(["rss"], "en").all()
        res_fi = App.objects.search(["rss"], "fi").all()
        self.assertEqual(len(res), 1)
        self.assertEqual(len(res_fi), 1)
        self.assertEqual(res.get(id="news").name, "News")
        self.assertEqual(res_fi.get(id="news").name, "Uutiset")

    def test_find_all(self):
        res = App.objects.search(["a"], "en").all()
        res_fi = App.objects.search(["a"], "fi").all()
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res_fi), 4)
        self.assertEqual(res.get(id="notes").name, "Notes")
        self.assertEqual(res_fi.get(id="notes").name, "Muistiinpanot")

    def test_multilang_terms(self):
        res = App.objects.search(["calendar", "sovellus"], "en").all()
        res_fi = App.objects.search(["app", "muistiinpano"], "fi").all()
        self.assertEqual(len(res), 0)
        self.assertEqual(len(res_fi), 0)

    def test_narrow_search(self):
        res = App.objects.search(["app"], "en").all()
        res_narrow = App.objects.search(["note", "app"], "en").all()
        self.assertEqual(len(res), 2)
        self.assertEqual(len(res_narrow), 1)

    def test_no_search_terms(self):
        res = App.objects.search([], "en").all()
        res_fi = App.objects.search([], "fi").all()
        self.assertEqual(len(res), 4)
        self.assertEqual(len(res_fi), 4)
        self.assertEqual(res.get(id="news").name, "News")
        self.assertEqual(res_fi.get(id="news").name, "Uutiset")
