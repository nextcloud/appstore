"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from datetime import datetime
from functools import reduce
from sys import maxsize
from typing import Any

from semantic_version import Spec, Version

SEMVER_REGEX = (
    r"(?:0|[1-9][0-9]*)" r"\.(?:0|[1-9][0-9]*)" r"\.(?:0|[1-9][0-9]*)" r"(?:\-(?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)


class AppSemVer:
    """
    Class used to sort a semantic version by nightly flags and released_at
    time
    """

    def __init__(self, version: str, is_nightly: bool = False, released_at: datetime | None = None) -> None:
        self.released_at = released_at
        self.is_nightly = is_nightly
        self.version = Version(version)

    def __lt__(self, other: "AppSemVer") -> bool:
        if self.version == other.version:
            if self.is_nightly and other.is_nightly and self.released_at and other.released_at:
                return self.released_at < other.released_at
            elif self.is_nightly:
                return False
            else:
                return True
        else:
            return self.version < other.version


def raw_version(version: str) -> str:
    """
    Returns the exact same version but replaces None with *
    :param version: version to adjust
    :return: raw version
    """
    if not version:
        return "*"
    else:
        return version


def pad_max_version(version: str) -> str:
    """
    Turns inclusive maximum versions into exclusiv semantic versions
    e.g.: 9 into 10.0.0, 9.0 into 9.1.0, 9.0.0 into 9.0.1
    :argument inclusive version maximum to pad
    :return an exclusive maximum version
    """
    if not version:
        return "*"

    parts = [int(part) for part in version.split(".")]
    if len(parts) == 1:
        parts[0] += 1
        parts += [0, 0]
    elif len(parts) == 2:
        parts[1] += 1
        parts += [0]
    elif len(parts) == 3:
        parts[2] += 1
    else:
        raise ValueError(f"Could not parse version {version}")
    return ".".join([str(part) for part in parts])


def pad_max_inc_version(version: str) -> str:
    """
    Turns non semver maximum versions into an inclusive maximum semantic
    version e.g.: 9 into 9.MAX_INT.MAX_INT, 9.0 into 9.1.MAX_INT,
    9.0.0 into 9.0.0
    :argument inclusive version maximum to pad
    :return an exclusive maximum version
    """
    if not version:
        return "*"

    while version.count(".") < 2:
        version += f".{maxsize}"
    return version


def pad_min_version(version: str) -> str:
    if not version:
        return "*"
    while version.count(".") < 2:
        version += ".0"
    return version


def to_raw_spec(min_version: str, max_version: str) -> str:
    """
    Combines minimum and maximum version into a raw spec
    :argument min_version: min version
    :argument max_version: max version
    :return: the spec
    """
    if max_version == "*" and min_version == "*":
        return "*"
    elif max_version == "*":
        return f">={min_version}"
    elif min_version == "*":
        return f"<={max_version}"
    else:
        return f">={min_version},<={max_version}"


def to_spec(min_version: str, max_version: str) -> str:
    """
    Combines minimum and maximum version into a spec. Requires semantic
    versions as strings
    :argument min_version: min version
    :argument max_version: max version
    :return: the spec
    """
    if max_version == "*" and min_version == "*":
        return "*"
    elif max_version == "*":
        return f">={min_version}"
    elif min_version == "*":
        return f"<{max_version}"
    else:
        return f">={min_version},<{max_version}"


GroupedVersions = dict[str, list[Any]]


def group_by_main_version(versions: GroupedVersions) -> GroupedVersions:
    """
    Groups a dict with semver version as key by their main version
    :param versions: dicts of version: value,
    e.g. {'9.0.1': [r1], '9.0.1': [r2]}
    :return: a grouped by main version dict, e.g. {'9': [r1, r2]}
    """

    def reduction(prev: Any, item: Any) -> Any:
        key, value = item
        main_version = str(Version(key).major)
        prev[main_version] = prev.get(main_version, []) + value
        return prev

    return reduce(reduction, versions.items(), {})


def version_in_spec(version: str, spec: str) -> bool:
    """
    Checks if a string version is in a spec
    :param version:
    :param spec:
    :return:
    """
    return Version(version) in Spec(spec)


_PHP_SPECIAL_FORMS = (
    (b"dev", 0),
    (b"alpha", 1),
    (b"a", 1),
    (b"beta", 2),
    (b"b", 2),
    (b"RC", 3),
    (b"rc", 3),
    (b"#", 4),
    (b"pl", 5),
    (b"p", 5),
)
_PHP_LONG_MAX = 2**63 - 1


def _is_digit(char: int) -> bool:
    return 0x30 <= char <= 0x39


def _is_alnum(char: int) -> bool:
    return _is_digit(char) or 0x41 <= char <= 0x5A or 0x61 <= char <= 0x7A


def _php_canonicalize_version(version: bytes) -> bytes:
    def is_digit(char: int) -> bool:
        return _is_digit(char) and char != 0x2E

    def is_non_digit(char: int) -> bool:
        return not _is_digit(char) and char != 0x2E

    result = bytearray(version[:1])
    previous = version[0]
    for char in version[1:]:
        if char in b"-_+":
            if result[-1] != 0x2E:
                result.append(0x2E)
        elif (is_non_digit(previous) and is_digit(char)) or (is_digit(previous) and is_non_digit(char)):
            if result[-1] != 0x2E:
                result.append(0x2E)
            result.append(char)
        elif not _is_alnum(char):
            if result[-1] != 0x2E:
                result.append(0x2E)
        else:
            result.append(char)
        previous = char
    if result[-1:] == b".":
        del result[-1]
    return bytes(result)


def _php_compare_special_forms(form1: bytes, form2: bytes) -> int:
    def order(form: bytes) -> int:
        return next((order for name, order in _PHP_SPECIAL_FORMS if form.startswith(name)), -1)

    difference = order(form1) - order(form2)
    return (difference > 0) - (difference < 0)


def _php_leading_number(part: bytes) -> int:
    digits = len(part) - len(part.lstrip(b"0123456789"))
    return min(int(part[:digits]), _PHP_LONG_MAX)


def _php_version_compare(version1: bytes, version2: bytes) -> int:
    if not version1 or not version2:
        return (len(version1) > 0) - (len(version2) > 0)
    version1 = version1 if version1.startswith(b"#") else _php_canonicalize_version(version1)
    version2 = version2 if version2.startswith(b"#") else _php_canonicalize_version(version2)
    position1 = position2 = 0
    dot1: int | None = 0
    dot2: int | None = 0
    compare = 0
    while position1 < len(version1) and position2 < len(version2) and dot1 is not None and dot2 is not None:
        dot1 = version1.find(b".", position1)
        dot1 = None if dot1 < 0 else dot1
        dot2 = version2.find(b".", position2)
        dot2 = None if dot2 < 0 else dot2
        part1 = version1[position1:dot1]
        part2 = version2[position2:dot2]
        numeric1 = part1[:1].isdigit()
        numeric2 = part2[:1].isdigit()
        if numeric1 and numeric2:
            number1 = _php_leading_number(part1)
            number2 = _php_leading_number(part2)
            compare = (number1 > number2) - (number1 < number2)
        elif not numeric1 and not numeric2:
            compare = _php_compare_special_forms(part1, part2)
        elif numeric1:
            compare = _php_compare_special_forms(b"#N#", part2)
        else:
            compare = _php_compare_special_forms(part1, b"#N#")
        if compare != 0:
            break
        if dot1 is not None:
            position1 = dot1 + 1
        if dot2 is not None:
            position2 = dot2 + 1
    if compare == 0:
        if dot1 is not None:
            rest = version1[position1:]
            compare = 1 if rest[:1].isdigit() else _php_version_compare(rest, b"#N#")
        elif dot2 is not None:
            rest = version2[position2:]
            compare = -1 if rest[:1].isdigit() else _php_version_compare(b"#N#", rest)
    return compare


def php_version_compare(version1: str, version2: str) -> int:
    """
    Compares two versions like PHP's version_compare(), which Nextcloud uses to pick the newest app release, as of
    PHP 8.4.22 and 8.5.7. Those ignore a trailing dot after canonicalisation, so "1.0.0-" equals "1.0.0". Earlier
    versions differ only for versions that end in a character other than an ASCII letter or digit.
    :return: -1, 0 or 1
    """
    return _php_version_compare(version1.encode(), version2.encode())
