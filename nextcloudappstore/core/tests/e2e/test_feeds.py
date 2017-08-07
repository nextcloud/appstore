from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


class FeedTest(BaseStoreTest):
    fixtures = [
        'categories.json',
        'databases.json',
        'licenses.json',
        'nextcloudreleases.json',
        'apps.json',
        'admin.json',
    ]

    def test_rss_all(self):
        self.go_to('home')

        rss_url = self.by_css('link[type="application/rss+xml"]')
        self.selenium.get(rss_url.get_attribute('href'))

        result = self.selenium.page_source

        # unfortunately there is no selenium API to get the response code
        # and firefox has custom rss feed handling so comparing the page
        # source won't work
        self.assertTrue(len(result) > 0)
        self.assertIn('News (10.1.0)', result)

    def test_atom_all(self):
        self.go_to('home')

        rss_url = self.by_css('link[type="application/atom+xml"]')
        self.selenium.get(rss_url.get_attribute('href'))

        result = self.selenium.page_source

        # unfortunately there is no selenium API to get the response code
        # and firefox has custom rss feed handling so comparing the page
        # source won't work
        self.assertTrue(len(result) > 0)
        self.assertIn('News (10.1.0)', result)
