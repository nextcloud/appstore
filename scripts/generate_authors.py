#!/usr/bin/env python3
import re
import subprocess
from os import pardir
from os.path import dirname, join, realpath
from typing import Iterator


def get_git_authors() -> list[str]:
    command = ["git", "--no-pager", "shortlog", "-nse", "HEAD"]
    authors = subprocess.check_output(command)
    return authors.decode("utf-8").split("\n")


def append_git_author(line: str, result_list: list[dict]) -> None:
    ignore = ["nextcloud bot", "[bot]"]
    format_regex = r"^\s*(?P<commit_count>\d+)\s*(?P<name>.*?)\s*<(" r"?P<email>[^\s]+)>$"
    result = re.search(format_regex, line)
    if result:
        name = result.group("name")
        for i in ignore:
            if name.lower().find(i) != -1:
                return
        present = next((item for item in result_list if item["name"] == name), None)
        if present:
            present["commits"] = str(int(present["commits"]) + int(result.group("commit_count")))
        else:
            result_list.append({"commits": result.group("commit_count"), "name": name, "email": result.group("email")})
    else:
        raise ValueError("Could not extract authors from line %s" % line)


def to_markdown(authors: Iterator[dict[str, str]]) -> tuple[str, str]:
    result = ["# Authors", ""]
    for author in authors:
        result += ["* [%s](mailto:%s)" % (author["name"], author["email"])]
    return "\n".join(result) + "\n", "md"


def to_rst(authors: Iterator[dict[str, str]]) -> tuple[str, str]:
    result = ["Authors", "=======", ""]
    for author in authors:
        result += ["* `%s <mailto:%s>`_" % (author["name"], author["email"])]
    return "\n".join(result) + "\n", "rst"


def get_authors_file(suffix: str) -> str:
    directory = dirname(realpath(__file__))
    directory = join(directory, pardir)
    return join(directory, "AUTHORS.%s" % suffix)


def main() -> None:
    authors = []
    for author in get_git_authors():
        if author:
            append_git_author(author, authors)
    text, extension = to_markdown(authors)
    with open(get_authors_file(extension), "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
