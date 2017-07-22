import time

from selenium.webdriver.support.select import Select

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


class CommentAppTest(BaseStoreTest):
    fixtures = ['admin.json', 'apps.json']

    def test_comment(self):
        self.login()
        self.go_to_app('news')
        self.by_id('toggle-comment-button').click()

        # rate bad
        self.by_id('id_rating_0').click()
        Select(self.by_id('id_language_code')).select_by_value('en')
        self.by_id('id_comment').send_keys('my comment')

        self.by_css('#app-ratings form input[type="submit"]').click()

        name = self.by_css('.rating-comment:first-child .author').text
        comment = self.by_css('.rating-comment:first-child .comment p').text

        self.assertEqual('Anonymous', name.strip())
        self.assertEqual('my comment', comment.strip())
