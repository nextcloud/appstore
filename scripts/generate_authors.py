#!/usr/bin/env python3
import re
import subprocess
from os import pardir
from os.path import dirname, join, realpath
from typing import Dict, Iterator, List, Tuple


def get_git_authors() -> List[str]:
    command = ['git', '--no-pager', 'shortlog', '-nse', 'HEAD']
    authors = subprocess.check_output(command)
    return authors.decode('utf-8').split('\n')


def parse_git_author(line: str) -> Dict[str, str]:
    format_regex = r'^\s*(?P<commit_count>\d+)\s*(?P<name>.*\w)\s*<(' \
                   r'?P<email>[^\s]+)>$'
    result = re.search(format_regex, line)
    if result:
        return {
            'commits': result.group('commit_count'),
            'name': result.group('name'),
            'email': result.group('email')
        }
    else:
        raise ValueError('Could not extract authors from line %s' % line)


def to_markdown(authors: Iterator[Dict[str, str]]) -> Tuple[str, str]:
    result = ['# Authors', '']
    for author in authors:
        result += ['* [%s](mailto:%s)' % (author['name'], author['email'])]
    return '\n'.join(result), 'md'


def to_rst(authors: Iterator[Dict[str, str]]) -> Tuple[str, str]:
    result = ['Authors', '=======', '']
    for author in authors:
        result += ['* `%s <mailto:%s>`_' % (author['name'], author['email'])]
    return '\n'.join(result), 'rst'


def get_authors_file(suffix: str) -> str:
    directory = dirname(realpath(__file__))
    directory = join(directory, pardir)
    return join(directory, 'AUTHORS.%s' % suffix)


def main() -> None:
    ignore = {'Nextcloud bot'}
    authors = get_git_authors()
    authors = filter(lambda name: name.strip() != '', authors)
    authors = [parse_git_author(author) for author in authors]
    authors = filter(lambda author: author['name'] not in ignore, authors)
    text, extension = to_markdown(authors)
    with open(get_authors_file(extension), 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main()
