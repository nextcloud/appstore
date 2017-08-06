from typing import Dict, Callable, Any

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from nextcloudappstore.core.tests.e2e import TEST_USER, TEST_EMAIL, \
    TEST_PASSWORD, SELENIUM_WAIT_SEC
from nextcloudappstore.user.facades import create_user, delete_user


class BaseStoreTest(StaticLiveServerTestCase):
    def by_id(self, id):
        return self.selenium.find_element_by_id(id)

    def by_css(self, selector):
        return self.selenium.find_element_by_css_selector(selector)

    def by_name(self, name: str):
        return self.selenium.find_element_by_name(name)

    def setUp(self):
        self.selenium = WebDriver()
        self.selenium.implicitly_wait(SELENIUM_WAIT_SEC)
        create_user(TEST_USER, TEST_PASSWORD, TEST_EMAIL)

    def tearDown(self):
        delete_user(TEST_USER)
        self.selenium.quit()
        super().tearDown()

    def go_to(self, url_name: str, kwargs: Dict[str, str] = None) -> None:
        app_url = reverse(url_name, kwargs=kwargs)
        self.selenium.get('%s%s' % (self.live_server_url, app_url))

    def go_to_app(self, app_id):
        self.go_to('app-detail', {'id': app_id})

    def go_to_app_register(self):
        self.go_to('app-register')

    def go_to_app_upload(self):
        self.go_to('app-upload')

    def login(self, user: str = TEST_USER, password: str = TEST_PASSWORD):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        user_input = self.selenium.find_element_by_name("login")
        user_input.send_keys(user)
        pass_input = self.selenium.find_element_by_name("password")
        pass_input.send_keys(password)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

    def wait_for(self, selector: str,
                 then: Callable[[WebElement], None]) -> Any:
        element = WebDriverWait(self.selenium, SELENIUM_WAIT_SEC).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        return then(element)
