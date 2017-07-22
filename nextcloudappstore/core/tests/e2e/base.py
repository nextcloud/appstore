from django.conf.global_settings import LOGIN_URL
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from nextcloudappstore.core.tests.e2e.facades import create_user, delete_user
from selenium.webdriver.firefox.webdriver import WebDriver

from nextcloudappstore.core.tests.e2e import TEST_USER, TEST_EMAIL, \
    TEST_PASSWORD


class BaseStoreTest(StaticLiveServerTestCase):

    def by_id(self, id):
        return self.selenium.find_element_by_id(id)

    def by_css(self, selector):
        return self.selenium.find_element_by_css_selector(selector)

    @classmethod
    def setUpClass(cls):
        super(BaseStoreTest, cls).setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(BaseStoreTest, cls).tearDownClass()

    def setUp(self):
        create_user(TEST_USER, TEST_PASSWORD, TEST_EMAIL)

    def tearDown(self):
        delete_user(TEST_USER)

    def go_to_app(self, app_id):
        app_url = reverse('app-detail', kwargs={'id': app_id})
        self.selenium.get('%s%s' % (self.live_server_url, app_url))

    def login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        user = self.selenium.find_element_by_name("login")
        user.send_keys(TEST_USER)
        password = self.selenium.find_element_by_name("password")
        password.send_keys(TEST_PASSWORD)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
