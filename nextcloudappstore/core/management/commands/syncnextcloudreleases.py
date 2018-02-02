import requests
from django.conf import settings
from django.core.management import BaseCommand
from django.core.management import CommandError

from nextcloudappstore.core.github import get_supported_releases, GitHubClient


class Command(BaseCommand):
    help = 'Queries Nextcloud\'s GitHub releases API to update all locally ' \
           'stored Nextcloud versions'

    def add_arguments(self, parser):
        parser.add_argument('--print', required=False, action='store_true',
                            help='Prints to stdout instead of importing '
                                 'releases into the database')
        parser.add_argument('--oldest-supported', required=True,
                            help='Oldest supported Nextcloud version')

    def handle(self, *args, **options):
        oldest_supported = options.get('oldest_supported')
        token = settings.GITHUB_API_TOKEN
        base_url = settings.GITHUB_API_BASE_URL


        try:
            client = GitHubClient(base_url, token)
            releases = get_supported_releases(client, oldest_supported)
        except requests.HTTPError as e:
            raise CommandError('Could not get releases: ' + str(e))

        if options['print']:
            for release in releases:
                self.stdout.write(release)
