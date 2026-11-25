"""
SPDX-FileCopyrightText: 2026 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import fcntl
import gzip
import json
import os
import tempfile
import time
import zlib
from contextlib import ExitStack, contextmanager

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from nextcloudappstore.api.v1.serializers import AppSerializer
from nextcloudappstore.api.v1.views import (
    apps_json_queryset,
    apps_json_snapshot,
    selectable_release_ids,
)

# Each list keeps file times of its own parity. A web server that derives the ETag from file time and size then never
# gives both lists the same ETag, so a server whose key becomes valid or invalid gets the other list, not a 304.
TIERS = (("community", 0), ("enterprise", 1))

# A list with more than this share fewer apps or releases than the file it replaces is not written without --force.
MAX_SHRINK = 0.1


class Command(BaseCommand):
    help = (
        "Builds apps.json without and with enterprise-only apps from one snapshot of the database, and writes each "
        "list with a gzipped copy next to it for the web server to serve. A list that has not changed is not rewritten."
    )

    def add_arguments(self, parser):
        parser.add_argument("--community", metavar="FILE", help="Where to write the list without enterprise-only apps")
        parser.add_argument("--enterprise", metavar="FILE", help="Where to write the list with enterprise-only apps")
        parser.add_argument(
            "--force",
            action="store_true",
            # argparse formats help texts with %, so a literal % is written as %%.
            help=(
                f"Write the lists even if one is empty or has more than {MAX_SHRINK:.0%}% fewer apps or releases "
                "than the file it replaces"
            ),
        )

    def handle(self, *args, **options):
        paths = {tier: options[tier] for tier, _ in TIERS if options[tier]}
        if not paths:
            raise CommandError("Give --community, --enterprise or both")
        files = [file for path in paths.values() for file in (path, path + ".gz")]
        if len({os.path.realpath(file) for file in files}) < len(files):
            raise CommandError("--community and --enterprise must be different files")
        for path in paths.values():
            if os.path.isdir(path):
                raise CommandError(f"{path} is a directory")
            if not os.path.isdir(_directory(path)):
                raise CommandError(f"The directory for {path} does not exist")

        self.verbosity = options["verbosity"]
        targets = {os.path.realpath(file) for file in files}
        with ExitStack() as locks:
            for directory in sorted({os.path.realpath(_directory(path)) for path in paths.values()}):
                locks.enter_context(_lock(directory))
            for path in paths.values():
                directory, prefix = _directory(path), _temporary_prefix(path)
                for name in os.listdir(directory):
                    leftover = os.path.join(directory, name)
                    if name.startswith(prefix) and os.path.realpath(leftover) not in targets:
                        os.unlink(leftover)
            self._build(paths, options["force"])

    def _build(self, paths, force):
        with apps_json_snapshot():
            apps = list(apps_json_queryset(selectable_release_ids()))
            data = AppSerializer(apps, many=True).data
        enterprise_only = {app.id for app in apps if app.is_enterprise_only}
        community = [item for item in data if item["id"] not in enterprise_only]
        lists = {"community": community, "enterprise": data if settings.ENABLE_ENTERPRISE_ONLY_APPS else community}

        if not force:
            for tier, path in paths.items():
                _check_size(tier, path, lists[tier], enterprise_only)

        renderer = CamelCaseJSONRenderer()
        for tier, parity in TIERS:
            if tier in paths:
                self._publish(tier, paths[tier], renderer.render(lists[tier]), _size(lists[tier]), parity)

    def _publish(self, tier, path, body, size, parity):
        listed = f"{tier}: {size[0]} apps with {size[1]} releases"
        mtime, gz_mtime = _mtime(path), _mtime(path + ".gz")
        if mtime is not None and mtime % 2 == parity and mtime == gz_mtime and _holds(path, body):
            if self.verbosity:
                self.stdout.write(f"{listed}, unchanged in {path}")
            return
        now = int(time.time())
        new_mtime = now - now % 2 + parity
        for previous in (mtime, gz_mtime):
            if previous is not None:
                # Later than the files it replaces, also if the clock went back, so the ETag is always new.
                new_mtime = max(new_mtime, previous + 1 + (parity - previous - 1) % 2)
        compressed = gzip.compress(body, compresslevel=9, mtime=new_mtime)
        _replace(path + ".gz", compressed, new_mtime)
        _replace(path, body, new_mtime)
        if self.verbosity:
            self.stdout.write(f"{listed}, {len(body)} bytes, {len(compressed)} gzipped, written to {path}")


def _directory(path):
    return os.path.dirname(os.path.abspath(path))


def _temporary_prefix(path):
    return f".{os.path.basename(path)}."


@contextmanager
def _lock(directory):
    """Locks the directory for one run. The community file is in the web root, so the lock is not a file."""
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise CommandError(f"Another run is writing to {directory}") from None
        yield
    finally:
        os.close(descriptor)


def _check_size(tier, path, apps, enterprise_only):
    previous = _previous_apps(path)
    if previous is not None:
        listed = {app["id"] for app in apps}
        # An app that became enterprise-only and left this list is not lost.
        previous = [app for app in previous if app["id"] not in enterprise_only or app["id"] in listed]
    if not apps:
        if previous == []:
            return
        raise CommandError(f"{tier}: no apps to list, so no list was written. Use --force to write it anyway")
    if previous is None:
        return
    new, old = _size(apps), _size(previous)
    if new[0] < old[0] * (1 - MAX_SHRINK) or new[1] < old[1] * (1 - MAX_SHRINK):
        raise CommandError(
            f"{tier}: {new[0]} apps with {new[1]} releases instead of {old[0]} with {old[1]} in {path}, so no list "
            "was written. Use --force to write it anyway"
        )


def _mtime(path):
    try:
        return int(os.stat(path).st_mtime)
    except FileNotFoundError:
        return None


def _read(path):
    with open(path, "rb") as file:
        return file.read()


def _holds(path, body):
    """Whether the file and its gzipped copy both hold the list."""
    try:
        return _read(path) == body and gzip.decompress(_read(path + ".gz")) == body
    except (OSError, EOFError, zlib.error):
        return False


def _size(apps):
    return len(apps), sum(len(app["releases"]) for app in apps)


def _previous_apps(path):
    """The apps in the file, or None if there is no file or it does not hold a list of apps."""
    try:
        apps = json.loads(_read(path))
        if isinstance(apps, list) and all(
            isinstance(app["releases"], list) and isinstance(app["id"], str) and app["id"] for app in apps
        ):
            return apps
    except (FileNotFoundError, ValueError, TypeError, KeyError):
        pass
    return None


def _replace(path, content, mtime):
    """Replaces the file in one step, so a reader gets either the old or the new file, never a part of one."""
    file = tempfile.NamedTemporaryFile(dir=_directory(path), prefix=_temporary_prefix(path), delete=False)
    try:
        with file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(file.name, 0o644)
        os.utime(file.name, (mtime, mtime))
        os.replace(file.name, path)
    except BaseException:
        os.unlink(file.name)
        raise
