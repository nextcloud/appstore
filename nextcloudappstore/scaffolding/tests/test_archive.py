import tarfile

from django.test import TestCase

from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.scaffolding.archive import build_archive, build_files


class ArchiveTest(TestCase):
    def setUp(self):
        self.args = {
            "name": "TheApp",
            "summary": "a summary",
            "description": "a description",
            "author_name": "author name",
            "author_email": "author email",
            "author_homepage": "author homepage",
            "issue_tracker": "https://test.com",
            "categories": ["tools"],
        }

    def test_build_files(self):
        expected = read_relative_file(__file__, "data/info.xml")
        result = build_files(self.args)
        info = result["theapp/appinfo/info.xml"]
        self.assertEqual(expected, info)
        self.assertNotIn("package-lock.json", result)
        self.assertNotIn("composer.lock", result)

    def test_build_archive(self):
        result = build_archive(self.args)
        expected = read_relative_file(__file__, "data/info.xml")
        with tarfile.open(fileobj=result, mode="r:gz") as f:
            member = f.getmember("theapp/appinfo/info.xml")
            with f.extractfile(member) as info:
                result = info.read().decode("utf-8")
                self.assertEqual(expected, result)
