import tarfile

from django.test import TestCase

from nextcloudappstore.core.facades import read_relative_file
from nextcloudappstore.scaffolding.archive import (
    apply_github_actions_fixer,
    build_archive,
    build_files,
)


class ArchiveTest(TestCase):
    def setUp(self):
        self.args = {
            "name": "TheApp",
            "summary": "a summary",
            "description": "a description",
            "author_name": "author name",
            "author_email": "author email",
            "author_homepage": "author homepage",
            "platform": "28",
            "issue_tracker": "https://test.com",
            "categories": ["tools"],
        }

    def test_build_files(self):
        with self.settings(APP_SCAFFOLDING_PROFILES={28: {"owncloud_version": "9.2"}}):
            expected = read_relative_file(__file__, "data/info.xml").strip()
            result = build_files(self.args)
            info = result["theapp/appinfo/info.xml"].strip()
            self.assertEqual(expected, info)

    def test_no_int_version(self):
        with self.assertRaises(ValueError):
            build_files({"platform": "test"})

    def test_no_directory(self):
        self.args["platform"] = "8"
        result = build_files(self.args)
        self.assertDictEqual({}, result)

    def test_build_archive(self):
        with self.settings(APP_SCAFFOLDING_PROFILES={28: {"owncloud_version": "9.2"}}):
            result = build_archive(self.args)
            expected = read_relative_file(__file__, "data/info.xml").strip()
            with tarfile.open(fileobj=result, mode="r:gz") as f:
                member = f.getmember("theapp/appinfo/info.xml")
                with f.extractfile(member) as info:
                    result = info.read().strip().decode("utf-8")
                    self.assertEqual(expected, result)

    def test_build_files_github_actions_format(self):
        for file_path, file_content in build_files(self.args).items():
            if file_path.find(".github/") != -1 and file_path.endswith(".yml"):
                assert not file_content.startswith("\n")
                assert not file_content.endswith("\n\n")
                assert file_content.endswith("\n")

    def test_apply_github_actions_fixer(self):
        for rel_path in (".github/CODE_OF_CONDUCT.md", ".github/workflows/reuse."):
            assert apply_github_actions_fixer(rel_path, "\nbody\n\n") == "\nbody\n\n"
        for rel_path in (".github/test.yml", ".github/workflows/test.yml"):
            assert apply_github_actions_fixer(rel_path, "\nbody\n\n") == "body\n"
        for file_content in ("body\n\n", "\nbody\n", "body\n"):
            assert apply_github_actions_fixer(".github/test.yml", file_content) == "body\n"
