import re
import tarfile
from io import BytesIO
from os import walk
from os.path import basename, isdir, join, relpath

from nextcloudappstore.core.facades import resolve_file_relative_path


def build_files(args: dict[str, str]) -> dict[str, str]:
    id = args["name"].lower()
    name = " ".join(re.findall(r"[A-Z][^A-Z]*", args["name"]))
    summary = args["summary"]
    description = args["description"]
    author_name = args["author_name"]
    author_mail = args["author_email"]
    author_homepage = args["author_homepage"]
    namespace = args["name"]
    categories = args["categories"]
    issue_tracker = args["issue_tracker"]
    patterns = {
        "app_template": id,
        "App Template": name,
        "AppTemplate": namespace,
        "An example summary": summary,
        "An example description": description,
        "<category>customization</category>": "\n\t".join(
            map(lambda category: f"<category>{category}</category>", categories)
        ),
        "<bugs>https://example.com/bugs</bugs>": f"<bugs>{issue_tracker}</bugs>",
        '"name": "example"': f'"name": "{author_name}"',
        '"email": "example@example.com"': f'"email": "{author_mail}"',
    }

    if author_homepage is not None:
        patterns['<author mail="example@example.com" homepage="https://example.com">Example</author>'] = (
            f'<author mail="{author_mail}" homepage="{author_homepage}">{author_name}</author>'
        )
        patterns['"homepage": "https://example.com"'] = f'"homepage": "{author_homepage}"'
    else:
        patterns['<author mail="example@example.com" homepage="https://example.com">Example</author>'] = (
            f'<author mail="{author_mail}">{author_name}</author>'
        )
        patterns['"homepage": "https://example.com"'] = f'"homepage": ""'

    base = resolve_file_relative_path(__file__, "app_template")
    result = {}
    if not isdir(base):
        return result

    for root, dirs, files in walk(base):
        for file in files:
            # Exclude lockfiles which are no longer valid after editing the content
            if basename(file) == "composer.lock" or basename(file) == "package-lock.json":
                continue

            file_path = join(root, file)
            rel_file_path = "{}/{}".format(id, relpath(file_path, base))
            with open(file_path, encoding="utf-8") as f:
                data = f.read()
                for pattern, replacement in patterns.items():
                    data = data.replace(pattern, replacement)

                result[rel_file_path] = data
    return result


def build_archive(parameters: dict[str, str]) -> BytesIO:
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as f:
        files = build_files(parameters)
        for path, contents in files.items():
            info = tarfile.TarInfo(path)
            encoded_content = contents.encode()
            info.size = len(encoded_content)
            f.addfile(info, BytesIO(encoded_content))
    buffer.seek(0)
    return buffer
