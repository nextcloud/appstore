from semantic_version import Version
import sys


def pad_max_version(version):
    """
    :argument version maximum version which is padded with the biggest number
    this is because you want the maximum version 9.1 to be valid for 9.1.1
    """
    while version.count('.') < 2:
        version += '.%i' % sys.maxsize
    return version


def pad_version(version):
    while version.count('.') < 2:
        version += '.0'
    return version


def includes_release(release, version_string):
    version = Version(pad_version(version_string))
    includes_min = True
    includes_max = True
    if release.platform_min_version:
        min_version = pad_version(release.platform_min_version)
        includes_min = Version(min_version) <= version
    if release.platform_max_version:
        max_version = pad_max_version((release.platform_max_version))
        includes_max = Version(max_version) >= version
    return includes_max and includes_min


def app_has_included_release(app, version_string):
    releases = app.releases.all()
    releases = filter(lambda r: includes_release(r, version_string), releases)
    return len(list(releases)) > 0
