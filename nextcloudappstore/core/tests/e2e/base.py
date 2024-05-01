from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as exp_cond
from selenium.webdriver.support.wait import WebDriverWait

from nextcloudappstore.core.tests.e2e import (
    SELENIUM_WAIT_SEC,
    TEST_EMAIL,
    TEST_PASSWORD,
    TEST_USER,
)
from nextcloudappstore.user.facades import create_user, delete_user


class BaseStoreTest(StaticLiveServerTestCase):
    def by_id(self, id):
        return self.selenium.find_element(By.ID, id)

    def by_css(self, selector: str, multiple: bool = False):
        if multiple:
            return self.selenium.find_elements(By.CSS_SELECTOR, selector)
        else:
            return self.selenium.find_element(By.CSS_SELECTOR, selector)

    def setUp(self):
        self.selenium = WebDriver()
        self.selenium.implicitly_wait(SELENIUM_WAIT_SEC)
        user = create_user(TEST_USER, TEST_PASSWORD, TEST_EMAIL)
        user.firstname = "live"
        user.lastname = "test"
        user.save()

    def tearDown(self):
        try:
            delete_user(TEST_USER)
        except Exception:
            pass
        super().tearDown()
        self.selenium.quit()

    def go_to(self, url_name: str, kwargs: dict[str, str] = None) -> None:
        app_url = reverse(url_name, kwargs=kwargs)
        self.selenium.get(f"{self.live_server_url}{app_url}")

    def go_to_app(self, app_id):
        self.go_to("app-detail", {"id": app_id})

    def go_to_app_register(self):
        self.go_to("app-register")

    def go_to_app_upload(self):
        self.go_to("app-upload")

    def go_to_login(self):
        self.selenium.get(f"{self.live_server_url}/login/")

    def login(self, user: str = TEST_USER, password: str = TEST_PASSWORD):
        self.go_to_login()
        user_input = self.selenium.find_element(By.NAME, "login")
        user_input.send_keys(user)
        pass_input = self.selenium.find_element(By.NAME, "password")
        pass_input.send_keys(password)
        self.selenium.find_element(By.XPATH, '//button[@type="submit"]').click()

    def assert_can_not_login(self):
        self.go_to("home")
        self.go_to_login()
        self.by_id("id_login").clear()
        self.by_id("id_login").send_keys("livetest")
        self.by_id("id_password").clear()
        self.by_id("id_password").send_keys("livetest")
        self.by_css('.auth-form button[type="submit"]').click()

        error = self.by_css(".auth-form .text-danger")
        self.assertTrue(error.is_displayed())
        self.assertOnPage("account_login")

    def logout(self):
        self.findNavigationLink("account_logout").click()

    def wait_for(self, selector: str, then: Callable[[WebElement], None]) -> Any:
        element = WebDriverWait(self.selenium, SELENIUM_WAIT_SEC).until(
            exp_cond.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )
        return then(element)

    def wait_for_url(self, url: str, timeout: int | None = None) -> Any:
        if timeout is None:
            timeout = SELENIUM_WAIT_SEC
        WebDriverWait(self.selenium, timeout).until(exp_cond.url_contains(url))

    def wait_for_url_match(self, url: str, timeout: int | None = None) -> Any:
        if timeout is None:
            timeout = SELENIUM_WAIT_SEC
        WebDriverWait(self.selenium, timeout).until(exp_cond.url_matches(url))

    def wait_for_url_to_be(self, url: str, timeout: int | None = None) -> Any:
        if timeout is None:
            timeout = SELENIUM_WAIT_SEC
        WebDriverWait(self.selenium, timeout).until(self._url_to_be(url))

    def assertOnPage(self, url_name: str, kwargs: dict[str, str] = None) -> None:
        parsed = urlparse(self.selenium.current_url)
        url = reverse(url_name, kwargs=kwargs)
        self.assertEqual(url, parsed.path)

    def findNavigationLink(self, url_name: str, kwargs: dict[str, str] = None):
        route = reverse(url_name, kwargs=kwargs)
        return self.by_css(f'#navbar-wrapper a[href="{route}"]')

    @staticmethod
    def _url_to_be(url: str) -> Callable[[Any], bool]:
        def _predicate(driver):
            return url.removesuffix("/") == str(driver.current_url).removesuffix("/")

        return _predicate
