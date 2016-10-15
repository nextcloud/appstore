from datetime import datetime
from sys import maxsize
from django.test import TestCase
from nextcloudappstore.core.versioning import pad_min_version, to_spec, \
    pad_max_version, pad_max_inc_version, raw_version, to_raw_spec, AppSemVer


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

    def test_pad_inc_maximum(self):
        self.assertEqual('*', pad_max_inc_version(''))
        self.assertEqual('9.%i.%i' % (maxsize, maxsize),
                         pad_max_inc_version('9'))
        self.assertEqual('9.0.%i' % maxsize, pad_max_inc_version('9.0'))
        self.assertEqual('9.0.0', pad_max_inc_version('9.0.0'))

    def test_to_spec(self):
        self.assertEqual('*', to_spec('*', '*'))
        self.assertEqual('>=9.0.0,<11.0.0', to_spec('9.0.0', '11.0.0'))
        self.assertEqual('>=9.0.0', to_spec('9.0.0', '*'))
        self.assertEqual('<11.0.0', to_spec('*', '11.0.0'))

    def test_raw(self):
        self.assertEqual('*', raw_version(''))
        self.assertEqual('9', raw_version('9'))

    def test_to_raw_spec(self):
        self.assertEqual('*', to_raw_spec('*', '*'))
        self.assertEqual('>=9,<=11', to_raw_spec('9', '11'))
        self.assertEqual('>=9', to_raw_spec('9', '*'))
        self.assertEqual('<=11', to_raw_spec('*', '11'))

    def test_semver(self):
        self.assertLess(AppSemVer('1.0.0'), AppSemVer('1.0.1'))

    def test_semver_nightly(self):
        self.assertLess(AppSemVer('1.0.0'), AppSemVer('1.0.0', True))

    def test_semver_nightly_other(self):
        self.assertGreater(AppSemVer('1.0.0', True), AppSemVer('1.0.0'))

    def test_semver_two_nightlies(self):
        d1 = datetime.now()
        d2 = datetime.now()
        self.assertLess(AppSemVer('1.0.0', True, d1),
                        AppSemVer('1.0.0', True, d2))

    def test_semver_max(self):
        v1 = AppSemVer('1.0.0', True, datetime.now())
        v2 = AppSemVer('1.0.0', True, datetime.now())
        v3 = AppSemVer('0.9.9', True, datetime.now())
        v4 = AppSemVer('1.0.0')
        versions = [v1, v3, v2, v4]
        self.assertEqual(v2, max(versions))
