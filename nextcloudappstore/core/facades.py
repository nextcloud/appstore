import os
from itertools import chain

"""
Contains small utility and shortcut functions
"""


def resolve_file_relative_path(file_path: str, target_path: str) -> str:
    """
    Allows you to resolve a file path relative to the current file
    :param file_path: most of the time __file__, file path from which you
    want to resolve the target_path
    :param target_path: relative path to the target path
    :return: the absolute path to the target_path
    """
    dirname, filename = os.path.split(os.path.abspath(file_path))
    return os.path.join(dirname, target_path)


def read_file_contents(file_path: str) -> str:
    """
    Small wrapper for reading text from a file
    :param file_path: the path to the file
    :return: the read text
    """
    with open(file_path, 'r') as f:
        result = f.read()
    return result


def read_relative_file(file_path: str, target_path: str) -> str:
    """
    Small wrapper for reading text from a relative file
    :param file_path: most of the time __file__, file path from which you
    want to resolve the target_path
    :param file_path: the path to the file
    :return: the read text
    """
    file = resolve_file_relative_path(file_path, target_path)
    return read_file_contents(file)


def flatmap(f, xs):
    return chain.from_iterable(map(f, xs))


def any_match(predicate, iterable) -> bool:
    """
    :param predicate: function to test items
    :param iterable: iterable
    :return: true if a predicate returns true for at least one element in an
     iterable
    """
    for entry in iterable:
        if predicate(entry):
            return True
    return False


def distinct(iterable, criteria=id):
    """
    :param iterable:
    :param criteria: by default the object in the list. Pass a lambda to choose
    a custom distinctness criteria
    :return: a distinct iterator of elements from an iterable
    """
    occurred_values = set()
    for element in iterable:
        value = criteria(element)
        if value not in occurred_values:
            occurred_values.add(value)
            yield element
