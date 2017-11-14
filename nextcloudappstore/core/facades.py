import os
from itertools import chain
from typing import Iterable, TypeVar, Callable, Set

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


def write_relative_file(file_path: str, target_path: str,
                        content: str) -> None:
    """
    Similar to read_relative_file but for writing
    :param file_path: most of the time __file__, file path from which you
    want to resolve the target_path
    :param target_path: the path to the file
    :param content: the text to write
    :return:
    """
    file = resolve_file_relative_path(file_path, target_path)
    with open(file, 'w') as f:
        f.write(content)


T = TypeVar('T')
U = TypeVar('U')


def flatmap(f: Callable[[T], Iterable[U]], xs: Iterable[T]) -> Iterable[U]:
    return chain.from_iterable(map(f, xs))


def any_match(predicate: Callable[[T], bool], iterable: Iterable[T]) -> bool:
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


def distinct(iterable: Iterable[T],
             criteria: Callable[[T], U]) -> Iterable[T]:
    """
    :param iterable:
    :param criteria: by default the object in the list. Pass a lambda to choose
    a custom distinctness criteria
    :return: a distinct iterator of elements from an iterable
    """
    occurred_values = set()  # type: Set[U]
    for element in iterable:
        value = criteria(element)
        if value not in occurred_values:
            occurred_values.add(value)
            yield element
