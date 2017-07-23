from enum import Enum

from selenium.webdriver.support.select import Select

from nextcloudappstore.core.tests.e2e.base import BaseStoreTest


class Rating(Enum):
    BAD = 'id_rating_0'
    OK = 'id_rating_1'
    GOOD = 'id_rating_1'


class CommentAppTest(BaseStoreTest):
    fixtures = [
        'categories.json',
        'databases.json',
        'licenses.json',
        'nextcloudreleases.json',
        'admin.json',
        'apps.json',
    ]

    def test_comment(self):
        self.login()
        self.go_to_app('news')

        self._rate(Rating.BAD, 'my comment')

        name = self.by_css('.rating-comment:first-child .author').text
        comment = self.by_css('.rating-comment:first-child .comment p').text
        self.assertEqual('Anonymous', name.strip())
        self.assertEqual('my comment', comment.strip())

    def _rate(self, rating: Rating, comment: str) -> None:
        self.by_id('toggle-comment-button').click()
        self.by_id(rating.value).click()
        Select(self.by_id('id_language_code')).select_by_value('en')
        self.by_id('id_comment').send_keys(comment)
        self.by_css('#app-ratings form input[type="submit"]').click()
