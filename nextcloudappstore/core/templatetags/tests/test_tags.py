"""
SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from django.test import TestCase

from nextcloudappstore.core.templatetags.app_rating_class import app_rating_class
from nextcloudappstore.core.templatetags.first_word import first_word
from nextcloudappstore.core.templatetags.markdown import markdown
from nextcloudappstore.core.templatetags.version_spec import version_spec


class TemplateTagsTestCase(TestCase):
    def test_version_spec(self):
        self.assertEqual("", version_spec("*"))
        self.assertEqual("3", version_spec("3"))

    def test_markdown(self):
        self.assertEqual("<h1>Hi</h1>", markdown("# Hi"))

    def test_first_word(self):
        self.assertEqual("test", first_word("test in here"))
        self.assertEqual("", first_word(""))

    def test_rating_class(self):
        self.assertEqual("very-negative-rating", app_rating_class(-1))
        self.assertEqual("very-negative-rating", app_rating_class(0))
        self.assertEqual("very-negative-rating", app_rating_class(0.2))
        self.assertEqual("negative-rating", app_rating_class(0.4))
        self.assertEqual("neutral-rating", app_rating_class(0.6))
        self.assertEqual("positive-rating", app_rating_class(0.8))
        self.assertEqual("very-positive-rating", app_rating_class(1))
        self.assertEqual("very-positive-rating", app_rating_class(2))
