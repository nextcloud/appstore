"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

from bleach import clean
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse, reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import gettext_lazy as _  # type: ignore
from markdown import markdown
from parler.models import TranslationDoesNotExist

from nextcloudappstore.core.models import AppRelease


class AppReleaseRssFeed(Feed):
    title = _("Newest app releases")
    description = _("Get the newest app release updates")
    link = reverse_lazy("home")

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def items(self):
        queryset = AppRelease.objects.order_by("-last_modified")
        if "nightly" not in self.request.GET:
            queryset = queryset.filter(is_nightly=False)
        if "prerelease" not in self.request.GET:
            queryset = queryset.exclude(version__contains="-")
        if "app" in self.request.GET:
            queryset = queryset.filter(app__id=self.request.GET.get("app"))
        return queryset[:10]

    def item_title(self, item):
        return f"{item.app.name} ({item.version})"

    def item_description(self, item):
        try:
            if item.changelog:
                changelog = "\n\n# {}\n\n{}".format(_("Changes"), item.changelog)
            else:
                changelog = ""
            content = f"{item.app.description}{changelog}"
        except TranslationDoesNotExist:
            content = item.app.description
        content += "\n\n [{}]({})".format(_("Download"), item.download)
        return clean(
            markdown(content), attributes=settings.MARKDOWN_ALLOWED_ATTRIBUTES, tags=settings.MARKDOWN_ALLOWED_TAGS
        )

    def item_guid(self, obj):
        nightly = "-nightly" if obj.is_nightly else ""
        return f"{obj.app.id}-{obj.version}{nightly}"

    def item_link(self, item):
        return reverse("app-detail", kwargs={"id": item.app.id})

    def item_author_name(self, item):
        return f"{item.app.owner.first_name} {item.app.owner.last_name}"

    def item_pubdate(self, item):
        return item.last_modified

    def item_updateddate(self, item):
        return item.last_modified


class AppReleaseAtomFeed(AppReleaseRssFeed):
    feed_type = Atom1Feed
    subtitle = AppReleaseRssFeed.description
