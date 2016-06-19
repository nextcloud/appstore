from django.test import TestCase
from nextcloudappstore.core.versioning import pad_min_version, to_spec, \
    pad_max_version


class VersioningTest(TestCase):
    def test_pad_maximum(self):
        self.assertEqual('*', pad_max_version(''))
        self.assertEqual('10.0.0', pad_max_version('9'))
        self.assertEqual('9.1.0', pad_max_version('9.0'))
        self.assertEqual('9.0.1', pad_max_version('9.0.0'))
        with self.assertRaises(ValueError):
            pad_max_version('9.0.0.0')

    def test_pad_minimum(self):
        self.assertEqual('*', pad_min_version(''))
        self.assertEqual('9.0.0', pad_min_version('9'))
        self.assertEqual('9.0.0', pad_min_version('9.0'))
        self.assertEqual('9.0.0', pad_min_version('9.0.0'))

    def test_to_spec(self):
        self.assertEqual('*', to_spec('*', '*'))
        self.assertEqual('>=9.0.0,<11.0.0', to_spec('9.0.0', '11.0.0'))
        self.assertEqual('>=9.0.0', to_spec('9.0.0', '*'))
        self.assertEqual('<11.0.0', to_spec('*', '11.0.0'))
