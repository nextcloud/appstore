from sys import maxsize


def raw_version(version: str) -> str:
    """
    Returns the exact same version but replaces None with *
    :param version: version to adjust
    :return: raw version
    """
    if not version:
        return '*'
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
        return '*'

    parts = [int(part) for part in version.split('.')]
    if len(parts) == 1:
        parts[0] += 1
        parts += [0, 0]
    elif len(parts) == 2:
        parts[1] += 1
        parts += [0]
    elif len(parts) == 3:
        parts[2] += 1
    else:
        raise ValueError('Could not parse version %s' % version)
    return '.'.join([str(part) for part in parts])


def pad_max_inc_version(version: str) -> str:
    """
    Turns non semver maximum versions into an inclusive maximum semantic
    version e.g.: 9 into 9.MAX_INT.MAX_INT, 9.0 into 9.1.MAX_INT,
    9.0.0 into 9.0.0
    :argument inclusive version maximum to pad
    :return an exclusive maximum version
    """
    if not version:
        return '*'

    while version.count('.') < 2:
        version += '.%i' % maxsize
    return version


def pad_min_version(version: str) -> str:
    if not version:
        return '*'
    while version.count('.') < 2:
        version += '.0'
    return version


def to_raw_spec(min_version: str, max_version: str) -> str:
    """
    Combines minimum and maximum version into a raw spec
    :argument min_version: min version
    :argument max_version: max version
    :return: the spec
    """
    if max_version == '*' and min_version == '*':
        return '*'
    elif max_version == '*':
        return '>=%s' % min_version
    elif min_version == '*':
        return '<=%s' % max_version
    else:
        return '>=%s,<=%s' % (min_version, max_version)


def to_spec(min_version: str, max_version: str) -> str:
    """
    Combines minimum and maximum version into a spec. Requires semantic
    versions as strings
    :argument min_version: min version
    :argument max_version: max version
    :return: the spec
    """
    if max_version == '*' and min_version == '*':
        return '*'
    elif max_version == '*':
        return '>=%s' % min_version
    elif min_version == '*':
        return '<%s' % max_version
    else:
        return '>=%s,<%s' % (min_version, max_version)
