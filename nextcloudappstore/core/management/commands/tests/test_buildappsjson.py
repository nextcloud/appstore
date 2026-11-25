"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import fcntl
import gzip
import json
import os
import tempfile
from io import StringIO
from unittest import skipUnless
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.db import connection, connections
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from nextcloudappstore.api.v1.views import selectable_release_ids
from nextcloudappstore.core.models import (
    App,
    AppAuthor,
    AppRelease,
    AppReleaseTranslation,
    AppTranslation,
    Database,
    DatabaseDependency,
    License,
    PhpExtension,
    PhpExtensionDependency,
    Screenshot,
    Video,
)


def create_app(owner, pk, is_enterprise_only=False, versions=("1.0.0",)):
    app = App.objects.create(pk=pk, owner=owner, is_enterprise_only=is_enterprise_only)
    for version in versions:
        AppRelease.objects.create(
            app=app,
            version=version,
            platform_version_spec=">=26.0.0",
            raw_platform_version_spec=">=26.0.0",
            php_version_spec="*",
            raw_php_version_spec="*",
        )
    return app


# Without a key validator, as when the web server checks the keys itself.
@override_settings(
    ENABLE_ENTERPRISE_ONLY_APPS=True, ENTERPRISE_KEY_VALIDATION_ENDPOINT="", ENTERPRISE_KEY_VALIDATION_API_KEY=""
)
class BuildAppsJsonTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="test", password="test", email="test@test.com")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name
        self.community = os.path.join(self.directory, "community.json")
        self.enterprise = os.path.join(self.directory, "enterprise.json")

    def build(self, *args, now=1_800_000_000):
        out = StringIO()
        with patch("nextcloudappstore.core.management.commands.buildappsjson.time.time", return_value=now):
            call_command(
                "buildappsjson", f"--community={self.community}", f"--enterprise={self.enterprise}", *args, stdout=out
            )
        return out.getvalue()

    def read(self, path):
        with open(path, "rb") as file:
            return file.read()

    def ids(self, path):
        return [app["id"] for app in json.loads(self.read(path))]

    def test_writes_both_lists_and_their_gzipped_copies(self):
        create_app(self.user, "news")
        create_app(self.user, "governance", is_enterprise_only=True)
        self.build()
        self.assertEqual(["news"], self.ids(self.community))
        self.assertEqual(["governance", "news"], self.ids(self.enterprise))
        for path in (self.community, self.enterprise):
            self.assertEqual(self.read(path), gzip.decompress(self.read(path + ".gz")))
            self.assertEqual(0o644, os.stat(path).st_mode & 0o777)
            self.assertEqual(0o644, os.stat(path + ".gz").st_mode & 0o777)
        self.assertEqual(
            ["community.json", "community.json.gz", "enterprise.json", "enterprise.json.gz"],
            sorted(os.listdir(self.directory)),
        )

    @override_settings(ENABLE_ENTERPRISE_ONLY_APPS=False)
    def test_lists_no_enterprise_only_app_while_the_feature_is_off(self):
        create_app(self.user, "news")
        create_app(self.user, "governance", is_enterprise_only=True)
        self.build()
        self.assertEqual(["news"], self.ids(self.community))
        self.assertEqual(["news"], self.ids(self.enterprise))

    def test_lists_integrations_without_releases(self):
        App.objects.create(pk="outlook", owner=self.user, is_integration=True)
        self.build()
        self.assertEqual(["outlook"], self.ids(self.community))

    def test_lists_are_what_the_api_returns_without_and_with_a_valid_key(self):
        create_app(self.user, "news", versions=("1.0.0", "1.1.0"))
        create_app(self.user, "governance", is_enterprise_only=True)
        self.build()
        client = APIClient()
        self.assertEqual(self.read(self.community), client.get(reverse("api:v1:apps")).content)
        with patch("nextcloudappstore.core.enterprise.validate_subscription_key", return_value=True):
            response = client.get(reverse("api:v1:apps"), HTTP_X_NC_SUBSCRIPTION_KEY="valid")
        self.assertEqual(self.read(self.enterprise), response.content)

    def test_lists_apps_and_what_they_contain_in_a_fixed_order(self):
        news = create_app(self.user, "news")
        create_app(self.user, "calendar")
        for language in ("fr", "de"):
            AppTranslation.objects.create(
                master=news, language_code=language, name=language, summary="", description=""
            )
        # Stored out of id order, and with names in neither order, so the order in the list can only come from the ids.
        second = AppAuthor.objects.create(id=1001, name="a-second")
        first = AppAuthor.objects.create(id=1000, name="b-first")
        news.authors.set([second, first])
        for model in (Screenshot, Video):
            for id in (1001, 1000):
                model.objects.create(id=id, app=news, url=f"https://example.com/{id}", ordering=1)
        release = news.releases.get()
        for language in ("fr", "de"):
            AppReleaseTranslation.objects.create(master=release, language_code=language)
        mit, agpl = License.objects.get_or_create(id="mit")[0], License.objects.get_or_create(id="agpl")[0]
        release.licenses.set([mit, agpl])
        for id, extension in ((1001, "curl"), (1000, "zip")):
            PhpExtensionDependency.objects.create(
                id=id, app_release=release, php_extension=PhpExtension.objects.get_or_create(id=extension)[0]
            )
        for id, database in ((1001, "sqlite"), (1000, "pgsql")):
            DatabaseDependency.objects.create(
                id=id, app_release=release, database=Database.objects.get_or_create(id=database, name=database)[0]
            )
        self.build()
        apps = json.loads(self.read(self.enterprise))
        self.assertEqual(["calendar", "news"], [app["id"] for app in apps])
        self.assertEqual(["de", "fr"], list(apps[1]["translations"]))
        self.assertEqual(["b-first", "a-second"], [author["name"] for author in apps[1]["authors"]])
        expected = ["https://example.com/1000", "https://example.com/1001"]
        self.assertEqual(expected, [screenshot["url"] for screenshot in apps[1]["screenshots"]])
        self.assertEqual(expected, [video["url"] for video in apps[1]["videos"]])
        release = apps[1]["releases"][0]
        self.assertEqual(["de", "fr"], list(release["translations"]))
        self.assertEqual(["agpl", "mit"], release["licenses"])
        self.assertEqual(["zip", "curl"], [extension["id"] for extension in release["phpExtensions"]])
        self.assertEqual(["pgsql", "sqlite"], [database["id"] for database in release["databases"]])

    def test_does_not_rewrite_an_unchanged_list(self):
        create_app(self.user, "news")
        self.build()
        before = {path: os.stat(path) for path in (self.community, self.enterprise)}
        output = self.build(now=1_800_000_900)
        self.assertIn("community: 1 apps with 1 releases, unchanged", output)
        self.assertIn("enterprise: 1 apps with 1 releases, unchanged", output)
        for path, stat in before.items():
            self.assertEqual((stat.st_ino, stat.st_mtime), (os.stat(path).st_ino, os.stat(path).st_mtime))

    def test_gives_each_list_file_times_of_its_own_parity(self):
        create_app(self.user, "news")
        self.build(now=1_800_000_001)
        self.assertEqual(self.read(self.community), self.read(self.enterprise))
        for path, mtime in ((self.community, 1_800_000_000), (self.enterprise, 1_800_000_001)):
            self.assertEqual(mtime, os.stat(path).st_mtime)
            self.assertEqual(mtime, os.stat(path + ".gz").st_mtime)

    def test_gives_a_changed_list_a_new_file_time_within_the_same_second(self):
        create_app(self.user, "news")
        self.build()
        create_app(self.user, "calendar")
        self.build()
        self.assertEqual(["calendar", "news"], self.ids(self.community))
        self.assertEqual(1_800_000_002, os.stat(self.community).st_mtime)
        self.assertEqual(1_800_000_003, os.stat(self.enterprise).st_mtime)

    def test_gives_a_new_file_time_that_neither_file_had(self):
        create_app(self.user, "news")
        self.build()
        create_app(self.user, "calendar")
        os.utime(self.community + ".gz", (1_800_000_002, 1_800_000_002))
        self.build()
        self.assertEqual(1_800_000_004, os.stat(self.community).st_mtime)
        self.assertEqual(1_800_000_004, os.stat(self.community + ".gz").st_mtime)

    def test_rewrites_a_list_whose_gzipped_copy_is_missing(self):
        create_app(self.user, "news")
        self.build()
        os.remove(self.community + ".gz")
        output = self.build(now=1_800_000_900)
        self.assertIn("community: 1 apps with 1 releases, ", output)
        self.assertNotIn("unchanged in " + self.community, output)
        self.assertEqual(self.read(self.community), gzip.decompress(self.read(self.community + ".gz")))

    def test_rewrites_a_list_whose_gzipped_copy_is_cut_short(self):
        create_app(self.user, "news")
        self.build()
        with open(self.community + ".gz", "r+b") as file:
            file.truncate(100)
        os.utime(self.community + ".gz", (1_800_000_000, 1_800_000_000))
        self.build(now=1_800_000_900)
        self.assertEqual(self.read(self.community), gzip.decompress(self.read(self.community + ".gz")))

    def test_rewrites_a_list_whose_gzipped_copy_has_another_file_time(self):
        create_app(self.user, "news")
        self.build()
        os.utime(self.community + ".gz", (1_800_000_100, 1_800_000_100))
        self.build(now=1_800_000_900)
        self.assertEqual(1_800_000_900, os.stat(self.community).st_mtime)
        self.assertEqual(1_800_000_900, os.stat(self.community + ".gz").st_mtime)

    def test_gives_a_later_file_time_after_the_clock_went_back(self):
        create_app(self.user, "news")
        self.build(now=1_800_000_900)
        create_app(self.user, "calendar")
        self.build(now=1_800_000_000)
        self.assertEqual(1_800_000_902, os.stat(self.community).st_mtime)
        self.assertEqual(1_800_000_903, os.stat(self.enterprise).st_mtime)

    def test_gives_each_change_within_a_second_its_own_file_time(self):
        create_app(self.user, "news")
        times = []
        for rating, now in ((0.6, 1_800_000_000), (0.7, 1_800_000_000), (0.8, 1_800_000_001)):
            App.objects.filter(pk="news").update(rating_overall=rating)
            self.build(now=now)
            times.append(os.stat(self.community).st_mtime)
        self.assertEqual([1_800_000_000, 1_800_000_002, 1_800_000_004], times)

    def test_gives_a_file_time_later_than_both_files_it_replaces(self):
        create_app(self.user, "news")
        self.build()
        os.utime(self.community, (1_800_000_501, 1_800_000_501))
        os.utime(self.community + ".gz", (1_800_000_100, 1_800_000_100))
        self.build()
        self.assertEqual(1_800_000_502, os.stat(self.community).st_mtime)
        self.assertEqual(1_800_000_502, os.stat(self.community + ".gz").st_mtime)

    def test_rewrites_a_list_whose_plain_file_holds_another_list(self):
        create_app(self.user, "news")
        self.build()
        with open(self.community, "w") as file:
            file.write("[]")
        os.utime(self.community, (1_800_000_000, 1_800_000_000))
        self.build(now=1_800_000_900)
        self.assertEqual(["news"], self.ids(self.community))

    def test_rewrites_a_list_whose_gzipped_copy_cannot_be_unpacked(self):
        create_app(self.user, "news")
        self.build()
        # Not gzip at all, and a gzip header followed by a block of a type deflate does not have.
        for content in (b"not gzip", b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03\x07"):
            with open(self.community + ".gz", "wb") as file:
                file.write(content)
            os.utime(self.community + ".gz", (os.stat(self.community).st_mtime,) * 2)
            self.build(now=1_800_000_900)
            self.assertEqual(self.read(self.community), gzip.decompress(self.read(self.community + ".gz")))

    def test_rewrites_a_list_whose_gzipped_copy_holds_another_list(self):
        create_app(self.user, "news")
        self.build()
        with open(self.community + ".gz", "wb") as file:
            file.write(gzip.compress(b"[]"))
        os.utime(self.community + ".gz", (1_800_000_000, 1_800_000_000))
        self.build(now=1_800_000_900)
        self.assertEqual(self.read(self.community), gzip.decompress(self.read(self.community + ".gz")))
        self.assertEqual(1_800_000_900, os.stat(self.community + ".gz").st_mtime)

    def test_rewrites_a_list_that_changed_but_kept_its_size(self):
        create_app(self.user, "news")
        self.build()
        App.objects.filter(pk="news").update(rating_overall=0.6)
        size = os.stat(self.community).st_size
        self.build(now=1_800_000_900)
        self.assertEqual(size, os.stat(self.community).st_size)
        self.assertEqual(0.6, json.loads(self.read(self.community))[0]["ratingOverall"])

    def test_repairs_a_list_left_half_written(self):
        create_app(self.user, "news")
        self.build()
        create_app(self.user, "calendar")
        replace = os.replace
        calls = []

        def fail_the_second(source, target):
            calls.append(target)
            if len(calls) == 2:
                raise OSError("disk full")
            replace(source, target)

        with patch("os.replace", fail_the_second), self.assertRaises(OSError):
            self.build(now=1_800_000_900)
        self.build(now=1_800_000_900)
        self.assertEqual(["calendar", "news"], self.ids(self.community))
        self.assertEqual(self.read(self.community), gzip.decompress(self.read(self.community + ".gz")))
        self.assertEqual(os.stat(self.community).st_mtime, os.stat(self.community + ".gz").st_mtime)

    def test_rewrites_a_list_written_with_the_other_parity(self):
        create_app(self.user, "news")
        self.build()
        os.utime(self.community, (1_800_000_001, 1_800_000_001))
        os.utime(self.community + ".gz", (1_800_000_001, 1_800_000_001))
        self.build(now=1_800_000_900)
        self.assertEqual(1_800_000_900, os.stat(self.community).st_mtime)

    def test_keeps_the_previous_lists_if_one_lost_many_apps(self):
        for pk in ("calendar", "mail", "news"):
            create_app(self.user, pk)
        self.build()
        before = {name: self.read(os.path.join(self.directory, name)) for name in os.listdir(self.directory)}
        App.objects.filter(pk__in=("calendar", "mail")).delete()
        with self.assertRaisesMessage(CommandError, "community: 1 apps with 1 releases instead of 3 with 3"):
            self.build(now=1_800_000_900)
        self.assertEqual(
            before, {name: self.read(os.path.join(self.directory, name)) for name in os.listdir(self.directory)}
        )
        self.build("--force", now=1_800_000_900)
        self.assertEqual(["news"], self.ids(self.community))

    def test_keeps_the_previous_lists_if_one_lost_many_releases(self):
        for pk in ("calendar", "mail", "news"):
            create_app(self.user, pk)
        self.build()
        with (
            patch("nextcloudappstore.core.management.commands.buildappsjson.selectable_release_ids", return_value=[]),
            self.assertRaisesMessage(CommandError, "community: 3 apps with 0 releases instead of 3 with 3"),
        ):
            self.build(now=1_800_000_900)
        self.assertEqual(1_800_000_000, os.stat(self.community).st_mtime)

    def test_keeps_the_previous_lists_if_the_enterprise_list_lost_many_apps(self):
        create_app(self.user, "news")
        for pk in ("governance", "dashboards", "audit"):
            create_app(self.user, pk, is_enterprise_only=True)
        self.build()
        App.objects.filter(pk__in=("dashboards", "audit")).delete()
        with self.assertRaisesMessage(CommandError, "enterprise: 2 apps with 2 releases instead of 4 with 4"):
            self.build(now=1_800_000_900)
        self.assertEqual(["audit", "dashboards", "governance", "news"], self.ids(self.enterprise))

    def test_leaves_apps_that_became_enterprise_only_out_of_the_community_list(self):
        for pk in ("calendar", "mail", "news"):
            create_app(self.user, pk)
        self.build()
        App.objects.filter(pk__in=("calendar", "mail")).update(is_enterprise_only=True)
        self.build(now=1_800_000_900)
        self.assertEqual(["news"], self.ids(self.community))
        self.assertEqual(["calendar", "mail", "news"], self.ids(self.enterprise))

    def test_leaves_enterprise_only_apps_out_of_the_enterprise_list_when_the_feature_is_switched_off(self):
        create_app(self.user, "news")
        for pk in ("governance", "dashboards"):
            create_app(self.user, pk, is_enterprise_only=True)
        self.build()
        with override_settings(ENABLE_ENTERPRISE_ONLY_APPS=False):
            self.build(now=1_800_000_900)
        self.assertEqual(["news"], self.ids(self.enterprise))

    def test_keeps_the_previous_lists_if_one_lost_many_apps_but_not_releases(self):
        for number in range(10):
            create_app(self.user, f"app{number}")
        self.build()
        App.objects.filter(pk__in=("app0", "app1")).delete()
        for spec in (">=27.0.0", ">=28.0.0"):
            AppRelease.objects.create(
                app_id="app2",
                version="2.0.0",
                platform_version_spec=spec,
                raw_platform_version_spec=spec,
                php_version_spec="*",
                raw_php_version_spec="*",
                is_nightly=spec == ">=28.0.0",
            )
        with self.assertRaisesMessage(CommandError, "community: 8 apps with 10 releases instead of 10 with 10"):
            self.build(now=1_800_000_900)

    def test_writes_an_empty_list_only_with_force(self):
        with self.assertRaisesMessage(CommandError, "community: no apps to list, so no list was written"):
            self.build()
        self.assertEqual([], os.listdir(self.directory))
        self.build("--force")
        self.assertEqual([], self.ids(self.community))
        self.build(now=1_800_000_900)

    def test_writes_an_empty_community_list_when_every_app_became_enterprise_only(self):
        create_app(self.user, "news")
        self.build()
        App.objects.filter(pk="news").update(is_enterprise_only=True)
        self.build(now=1_800_000_900)
        self.assertEqual([], self.ids(self.community))
        self.assertEqual(["news"], self.ids(self.enterprise))

    def test_checks_both_lists_before_writing_either(self):
        create_app(self.user, "news")
        for pk in ("governance", "dashboards", "audit"):
            create_app(self.user, pk, is_enterprise_only=True)
        self.build()
        create_app(self.user, "calendar")
        App.objects.filter(pk__in=("dashboards", "audit")).delete()
        with self.assertRaisesMessage(CommandError, "enterprise: 3 apps"):
            self.build(now=1_800_000_900)
        self.assertEqual(["news"], self.ids(self.community))

    def test_writes_a_list_with_at_most_a_tenth_fewer_apps(self):
        for number in range(10):
            create_app(self.user, f"app{number}")
        self.build()
        App.objects.filter(pk="app0").delete()
        self.build(now=1_800_000_900)
        self.assertEqual(9, len(self.ids(self.community)))
        App.objects.filter(pk="app1").delete()
        with self.assertRaisesMessage(CommandError, "community: 8 apps with 8 releases instead of 9 with 9"):
            self.build(now=1_800_001_800)

    def test_replaces_a_previous_file_that_is_not_a_list_of_apps(self):
        create_app(self.user, "news")
        for content in (
            "<html>",
            "[1, 2]",
            '{"a": 1}',
            '[{"id": "x"}]',
            '"apps"',
            "[[",
            '[{"releases": []}]',
            '[{"id": ["x"], "releases": []}]',
        ):
            for path in (self.community, self.enterprise):
                with open(path, "w") as file:
                    file.write(content)
            self.build()
            self.assertEqual(["news"], self.ids(self.community), content)

    def test_needs_a_file_in_an_existing_directory(self):
        with self.assertRaisesMessage(CommandError, "Give --community, --enterprise or both"):
            call_command("buildappsjson", stdout=StringIO())
        missing = os.path.join(self.directory, "missing", "apps.json")
        with self.assertRaisesMessage(CommandError, f"The directory for {missing} does not exist"):
            call_command("buildappsjson", f"--community={missing}", stdout=StringIO())
        with self.assertRaisesMessage(CommandError, f"{self.directory} is a directory"):
            call_command("buildappsjson", f"--community={self.directory}", stdout=StringIO())

    def test_needs_different_files_for_the_two_lists(self):
        create_app(self.user, "governance", is_enterprise_only=True)
        for same in (os.path.join(self.directory, ".", "community.json"), self.community + ".gz"):
            with self.assertRaisesMessage(CommandError, "--community and --enterprise must be different files"):
                call_command(
                    "buildappsjson", f"--community={self.community}", f"--enterprise={same}", stdout=StringIO()
                )
        self.assertEqual([], os.listdir(self.directory))

    def test_takes_both_files_in_one_directory_reached_through_a_link(self):
        create_app(self.user, "news")
        os.mkdir(os.path.join(self.directory, "real"))
        os.symlink("real", os.path.join(self.directory, "link"))
        call_command(
            "buildappsjson",
            f"--community={os.path.join(self.directory, 'real', 'community.json')}",
            f"--enterprise={os.path.join(self.directory, 'link', 'enterprise.json')}",
            stdout=StringIO(),
        )
        self.assertEqual(
            ["community.json", "community.json.gz", "enterprise.json", "enterprise.json.gz"],
            sorted(os.listdir(os.path.join(self.directory, "real"))),
        )

    def test_takes_a_relative_path(self):
        create_app(self.user, "news")
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.directory)
        call_command("buildappsjson", "--community=community.json", stdout=StringIO())
        self.assertEqual(["news"], self.ids(self.community))

    def test_prints_nothing_with_verbosity_0(self):
        create_app(self.user, "news")
        self.assertEqual("", self.build("--verbosity=0"))
        self.assertEqual(["news"], self.ids(self.community))

    def test_writes_only_the_lists_asked_for(self):
        create_app(self.user, "news")
        call_command("buildappsjson", f"--enterprise={self.enterprise}", stdout=StringIO())
        self.assertEqual(["enterprise.json", "enterprise.json.gz"], sorted(os.listdir(self.directory)))

    def test_refuses_to_run_while_another_run_writes_to_the_directory(self):
        create_app(self.user, "news")
        descriptor = os.open(self.directory, os.O_RDONLY)
        self.addCleanup(os.close, descriptor)
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        with self.assertRaisesMessage(CommandError, f"Another run is writing to {self.directory}"):
            self.build()
        self.assertEqual([], os.listdir(self.directory))
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        self.build()
        self.assertEqual(["news"], self.ids(self.community))

    def test_holds_an_exclusive_lock_on_both_directories_while_it_builds(self):
        create_app(self.user, "news")
        os.mkdir(os.path.join(self.directory, "other"))
        self.enterprise = os.path.join(self.directory, "other", "enterprise.json")
        locked = []

        def try_locks():
            for directory in (self.directory, os.path.join(self.directory, "other")):
                descriptor = os.open(directory, os.O_RDONLY)
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    locked.append(False)
                except BlockingIOError:
                    locked.append(True)
                finally:
                    os.close(descriptor)
            return selectable_release_ids()

        replace = os.replace

        def replace_and_try_locks(source, target):
            try_locks()
            replace(source, target)

        with (
            patch("nextcloudappstore.core.management.commands.buildappsjson.selectable_release_ids", try_locks),
            patch("os.replace", replace_and_try_locks),
        ):
            self.build()
        self.assertEqual([True] * 10, locked)

    def test_keeps_the_temporary_files_of_the_run_that_holds_the_lock(self):
        create_app(self.user, "news")
        leftover = os.path.join(self.directory, ".community.json.abc123")
        with open(leftover, "w") as file:
            file.write("partial")
        descriptor = os.open(self.directory, os.O_RDONLY)
        self.addCleanup(os.close, descriptor)
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        with self.assertRaises(CommandError):
            self.build()
        self.assertTrue(os.path.exists(leftover))

    def test_removes_temporary_files_left_by_a_run_that_was_killed(self):
        create_app(self.user, "news")
        names = (".community.json.abc123", ".community.json.gz.def456", ".enterprise.json.ghi789", ".other.json.jkl")
        for name in names:
            with open(os.path.join(self.directory, name), "w") as file:
                file.write("partial")
        self.build()
        self.assertEqual(
            [".other.json.jkl", "community.json", "community.json.gz", "enterprise.json", "enterprise.json.gz"],
            sorted(os.listdir(self.directory)),
        )

    def test_removes_temporary_files_a_failed_run_could_not_remove(self):
        create_app(self.user, "news")
        with (
            patch("os.replace", side_effect=OSError("disk full")),
            patch("os.unlink"),
            self.assertRaises(OSError),
        ):
            self.build()
        self.assertTrue(any(name.startswith(".community.json.") for name in os.listdir(self.directory)))
        self.build()
        self.assertEqual(
            ["community.json", "community.json.gz", "enterprise.json", "enterprise.json.gz"],
            sorted(os.listdir(self.directory)),
        )

    def test_removes_temporary_files_in_a_directory_with_glob_characters_in_its_name(self):
        create_app(self.user, "news")
        for name in ("site[1]", "site1"):
            os.mkdir(os.path.join(self.directory, name))
            with open(os.path.join(self.directory, name, ".community.json.abc123"), "w") as file:
                file.write("partial")
        call_command(
            "buildappsjson",
            f"--community={os.path.join(self.directory, 'site[1]', 'community.json')}",
            stdout=StringIO(),
        )
        self.assertEqual(
            ["community.json", "community.json.gz"], sorted(os.listdir(os.path.join(self.directory, "site[1]")))
        )
        self.assertEqual([".community.json.abc123"], os.listdir(os.path.join(self.directory, "site1")))

    def test_keeps_a_list_whose_name_looks_like_a_temporary_file_of_the_other(self):
        create_app(self.user, "news")
        for pk in ("governance", "dashboards", "audit"):
            create_app(self.user, pk, is_enterprise_only=True)
        self.enterprise = os.path.join(self.directory, ".community.json.enterprise")
        self.build()
        self.build(now=1_800_000_900)
        self.assertEqual(1_800_000_001, os.stat(self.enterprise).st_mtime)
        App.objects.filter(pk__in=("dashboards", "audit")).delete()
        with self.assertRaisesMessage(CommandError, "enterprise: 2 apps"):
            self.build(now=1_800_001_800)

    def test_writes_its_temporary_files_next_to_the_lists(self):
        create_app(self.user, "news")
        replace = os.replace
        sources = []

        def record(source, target):
            sources.append(os.path.dirname(source) == os.path.dirname(target))
            replace(source, target)

        with patch("os.replace", record):
            self.build()
        self.assertEqual([True] * 4, sources)

    def test_leaves_no_temporary_file_when_a_write_fails(self):
        create_app(self.user, "news")
        self.build()
        create_app(self.user, "calendar")
        with patch("os.replace", side_effect=OSError("disk full")), self.assertRaises(OSError):
            self.build(now=1_800_000_900)
        self.assertEqual(["news"], self.ids(self.community))
        self.assertEqual(
            ["community.json", "community.json.gz", "enterprise.json", "enterprise.json.gz"],
            sorted(os.listdir(self.directory)),
        )

    def tearDown(self):
        self.user.delete()


@skipUnless(connection.vendor == "postgresql", "SQLite reads a whole transaction from one snapshot")
class BuildAppsJsonSnapshotTest(TransactionTestCase):
    def test_keeps_a_release_deleted_while_it_builds(self):
        user = get_user_model().objects.create_user(username="test", password="test", email="test@test.com")
        create_app(user, "news", versions=("1.9.0", "1.10.0"))
        other_connection = connections.create_connection("default")
        self.addCleanup(other_connection.close)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = os.path.join(directory.name, "apps.json")

        def ids_then_delete_newest():
            ids = selectable_release_ids()
            with other_connection.cursor() as cursor:
                cursor.execute("DELETE FROM core_apprelease WHERE version = %s", ["1.10.0"])
            return ids

        with patch(
            "nextcloudappstore.core.management.commands.buildappsjson.selectable_release_ids", ids_then_delete_newest
        ):
            call_command("buildappsjson", f"--community={path}", stdout=StringIO())
        with open(path, "rb") as file:
            apps = json.loads(file.read())
        self.assertEqual(["1.10.0"], [release["version"] for release in apps[0]["releases"]])
