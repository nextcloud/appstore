from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Updates the first site with the given domain and creates or updates the GitHub social login application"

    def add_arguments(self, parser):
        social_meta = SocialApp._meta
        parser.add_argument("--github-secret", required=True, help=social_meta.get_field("secret").help_text)
        parser.add_argument("--github-client-id", required=True, help=social_meta.get_field("client_id").help_text)
        site_meta = Site._meta
        parser.add_argument("--domain", required=True, help=site_meta.get_field("domain").help_text)

    def handle(self, *args, **options):
        # set up site which is required for social login
        site = Site.objects.all()[0]
        site.domain = options["domain"]
        site.name = "Nextcloud App Store"
        site.save()
        # set up github
        app, created = SocialApp.objects.get_or_create(provider="github")
        app.name = "GitHub"
        app.secret = options["github_secret"]
        app.client_id = options["github_client_id"]
        app.sites.add(site)
        app.save()

        msg = "Successfully initialized social accounts"
        self.stdout.write(self.style.SUCCESS(msg))
