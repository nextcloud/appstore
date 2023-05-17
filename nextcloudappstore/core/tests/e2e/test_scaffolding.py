from django.test import tag

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


@tag("e2e")
class ScaffoldTest(BaseStoreTest):
    fixtures = [
        "categories.json",
        "nextcloudreleases.json",
    ]

    def test_scaffold(self):
        self.go_to("app-scaffold")
        self.by_id("id_name").send_keys("MyApp")
        self.by_id("id_author_name").send_keys("John Doe")
        self.by_id("id_author_email").send_keys("john@doe.com")
        self.by_id("id_author_homepage").send_keys("http://google.com")
        self.by_id("id_issue_tracker").send_keys("http://github.com")
        self.by_id("id_summary").send_keys("A new app")
        self.by_id("id_description").send_keys("This app does nothing")

        valid_elems = self.by_css("#app-generate-form *:valid", True)
        self.assertEqual(11, len(valid_elems))
        self.by_id("submit").click()
