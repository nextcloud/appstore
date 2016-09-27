import re
import tarfile
from io import BytesIO
from typing import Dict
from os.path import join, isdir, relpath
from os import walk

from django.template import Context
from django.template import Template

from nextcloudappstore.core.facades import resolve_file_relative_path


def build_files(args):
    platform = int(args['platform'])
    vars = {
        'id': args['name'].lower(),
        'summary': args['summary'],
        'description': args['description'],
        'name': ' '.join(re.findall(r'[A-Z][^A-Z]*', args['name'])),
        'namespace': args['name'],
        'author_name': args['author_name'],
        'author_mail': args['author_email'],
        'author_homepage': args['author_homepage'],
    }
    relative_base = 'app-templates/%i/app/' % platform
    base = resolve_file_relative_path(__file__, relative_base)

    context = Context({'app': vars})
    result = {}
    if isdir(base):
        for root, dirs, files in walk(base):
            for file in files:
                file_path = join(root, file)
                rel_file_path = '%s/%s' % (
                    vars['id'], relpath(file_path, base)
                )
                with open(file_path) as f:
                    t = Template(f.read())
                    result[rel_file_path] = t.render(context)

    return result


def create_archive(parameters: Dict[str, str]) -> BytesIO:
    # TODO: hash django user name and create archive for that
    buffer = BytesIO()
    with tarfile.open('', mode='w:gz') as f:
        pass
        # build_archive(parameters, f)
    return buffer
