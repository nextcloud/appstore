from django.conf import settings
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext_lazy as _  # type: ignore
from nextcloudappstore.core.models import AppRelease
from markdown import markdown
from bleach import clean


class AppReleaseRssFeed(Feed):
    title = _('Newest app releases')
    description = _('Get the newest app release updates')
    link = reverse_lazy('home')

    def items(self):
        return AppRelease.objects.order_by('-last_modified')[:10]

    def item_title(self, item):
        return '%s (%s)' % (item.app.name, item.version)

    def item_description(self, item):
        return clean(markdown(item.app.description),
                     attributes=settings.MARKDOWN_ALLOWED_ATTRIBUTES,
                     tags=settings.MARKDOWN_ALLOWED_TAGS)

    def item_link(self, item):
        return item.download

    def item_author_name(self, item):
        return '%s %s' % (item.app.owner.first_name, item.app.owner.last_name)

    def item_pubdate(self, item):
        return item.last_modified

    def item_updateddate(self, item):
        return item.last_modified


class AppReleaseAtomFeed(AppReleaseRssFeed):
    feed_type = Atom1Feed
    subtitle = AppReleaseRssFeed.description
