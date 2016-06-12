import os

"""
Contains small utility and shortcut functions
"""


def resolve_file_relative_path(file_path: str, target_path: str) -> str:
    """
    Allows you to resolve a file path relative to the current file
    :argument file_path most of the time __file__, file path from which you
    want to resolve the target_path
    :argument target_path relative path to the target path
    :return the absolute path to the target_path
    """
    dirname, filename = os.path.split(os.path.abspath(file_path))
    return os.path.join(dirname, target_path)


def read_file_contents(file_path: str) -> str:
    """
    Small wrapper for reading text from a file
    :argument file_path the path to the file
    :return the read text
    """
    with open(file_path, 'r') as f:
        result = f.read()
    return result


def read_relative_file(file_path: str, target_path: str) -> str:
    """
    Small wrapper for reading text from a relative file
    :argument file_path the path to the file
    :return the read text
    """
    file = resolve_file_relative_path(file_path, target_path)
    return read_file_contents(file)
