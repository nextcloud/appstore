import datetime
from functools import reduce
from itertools import chain

from django.conf import settings  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from django.db.models import FloatField  # type: ignore
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ForeignKey,
    IntegerField,
    Manager,
    ManyToManyField,
    Model,
    Q,
    TextField,
    URLField,
)
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # type: ignore
from packaging.version import InvalidVersion
from packaging.version import parse as parse_version
from parler.models import TranslatableManager  # type: ignore
from parler.models import TranslatableModel, TranslatedFields
from semantic_version import Spec, Version

from nextcloudappstore.core.facades import distinct
from nextcloudappstore.core.rating import compute_rating
from nextcloudappstore.core.versioning import (
    AppSemVer,
    group_by_main_version,
    pad_max_inc_version,
    pad_min_version,
)


class AppManager(TranslatableManager):
    def search(self, terms, lang):
        queryset = self.get_queryset().active_translations(lang).language(lang).distinct()
        predicates = map(
            lambda t: (
                Q(translations__name__icontains=t)
                | Q(translations__summary__icontains=t)
                | Q(translations__description__icontains=t)
            ),
            terms,
        )
        query = reduce(lambda x, y: x & y, predicates, Q())
        return queryset.filter(query)

    def get_compatible(self, platform_version, inclusive=False, prefetch=None, select=None):
        qs = App.objects
        if select is not None and len(select) > 0:
            qs = qs.select_related(*select)
        if prefetch is not None and len(prefetch) > 0:
            qs = qs.prefetch_related(*prefetch)

        def app_filter(app):
            for release in app.releases.all():
                if release.is_compatible(platform_version, inclusive):
                    return True
            return False

        return list(filter(app_filter, qs.all()))


class App(TranslatableModel):
    objects = AppManager()
    id = CharField(
        max_length=256,
        unique=True,
        primary_key=True,
        verbose_name=_("ID"),
        help_text=_("app ID, identical to folder name"),
    )
    categories = ManyToManyField("Category", verbose_name=_("Category"))
    translations = TranslatedFields(
        name=CharField(max_length=256, verbose_name=_("Name"), help_text=_("Rendered app name for users")),
        summary=CharField(
            max_length=256, verbose_name=_("Summary"), help_text=_("Short text describing the app's purpose")
        ),
        description=TextField(verbose_name=_("Description"), help_text=_("Will be rendered as Markdown")),
    )
    # resources
    user_docs = URLField(max_length=256, blank=True, verbose_name=_("User documentation URL"))
    admin_docs = URLField(max_length=256, blank=True, verbose_name=_("Admin documentation URL"))
    developer_docs = URLField(max_length=256, blank=True, verbose_name=_("Developer documentation URL"))
    issue_tracker = URLField(max_length=256, blank=True, verbose_name=_("Issue tracker URL"))
    website = URLField(max_length=256, blank=True, verbose_name=_("Homepage"))
    discussion = URLField(max_length=256, blank=True, verbose_name=_("Forum"))
    created = DateTimeField(auto_now_add=True, editable=False, verbose_name=_("Created at"))
    last_modified = DateTimeField(auto_now=True, editable=False, db_index=True, verbose_name=_("Updated at"))
    owner = ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_("App owner"), on_delete=CASCADE, related_name="owned_apps"
    )
    co_maintainers = ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, verbose_name=_("Co-Maintainers"), related_name="co_maintained_apps"
    )
    authors = ManyToManyField("AppAuthor", blank=True, related_name="apps", verbose_name=_("App authors"))
    is_featured = BooleanField(verbose_name=_("Featured"), default=False)
    is_orphan = BooleanField(verbose_name=_("Orphan"), default=False)
    rating_recent = FloatField(verbose_name=_("Recent rating"), default=0.5)
    rating_overall = FloatField(verbose_name=_("Overall rating"), default=0.5)
    rating_num_recent = IntegerField(verbose_name=_("Number of recently submitted ratings"), default=0)
    rating_num_overall = IntegerField(verbose_name=_("Number of overall submitted ratings"), default=0)
    last_release = DateTimeField(editable=False, db_index=True, verbose_name=_("Last release at"), default=timezone.now)
    certificate = TextField(verbose_name=_("Certificate"))
    ownership_transfer_enabled = BooleanField(
        verbose_name=_("Ownership transfer enabled"),
        default=False,
        help_text=_(
            "If enabled, a user can try to register the same app "
            "again using the public certificate and signature. If he "
            "does, the app will be transferred to him."
        ),
    )
    is_integration = BooleanField(verbose_name=_("Integration (i.e. Outlook plugin)"), default=False)
    approved = BooleanField(verbose_name=_("Used to approve integrations"), default=False)

    class Meta:
        verbose_name = _("App")
        verbose_name_plural = _("Apps")

    def __str__(self) -> str:
        return self.name

    def can_update(self, user: User) -> bool:
        return self.owner == user or user in self.co_maintainers.all()

    def can_delete(self, user: User) -> bool:
        return self.owner == user

    @property
    def discussion_url(self):
        if self.discussion:
            return self.discussion
        else:
            return "{}/c/apps/{}".format(settings.DISCOURSE_URL, self.id.replace("_", "-"))

    def _get_grouped_releases(self, get_release_func):
        releases = NextcloudRelease.objects.all()
        versions = map(lambda r: r.version, releases)
        compatible_releases = map(lambda v: (v, get_release_func(v)), versions)
        grouped_releases = group_by_main_version(dict(compatible_releases))
        # deduplicate releases
        result = {}
        for version, releases in grouped_releases.items():
            result[version] = list(distinct(releases, lambda r: r.version))
        return result

    def releases_by_platform_v(self):
        """Looks up all compatible stable releases for each platform
        version.

        Example of returned dict:

        {'9.1': [<AppRelease object>, <AppRelease object>],
        '9.0': [<AppRelease object>]}

        :return dict with all compatible stable releases for each platform
                version.
        """
        return self._get_grouped_releases(self.compatible_releases)

    def unstable_releases_by_platform_v(self):
        """Looks up all compatible unstable releases for each platform version.

        Example of returned dict:

        {'9.1': [<AppRelease object>, <AppRelease object>],
        '9.0': [<AppRelease object>]}

        :return dict with all compatible unstable releases for each platform
                version.
        """
        return self._get_grouped_releases(self.compatible_unstable_releases)

    def latest_releases_by_platform_v(self):
        """Looks up the latest stable and unstable release for each platform
        version, returns only platforms where present any of the release type.

        .. note:: if the stable version is equal or greater than unstable, only the stable version will be in result.

        Example of returned dict:

        {'9.1': {
            'stable': <AppRelease object>,
            'unstable': <AppRelease object>
        },
        '9.0': {
            'stable': <AppRelease object>
        }}

        :return dict with the latest stable and unstable release for each
                platform version.
        """
        stable = self.releases_by_platform_v()
        unstable = self.unstable_releases_by_platform_v()

        def filter_latest(pair):
            version, releases = pair
            return version, self._latest(releases)

        latest_stable = dict(map(filter_latest, stable.items()))
        latest_unstable = dict(map(filter_latest, unstable.items()))
        all_versions = set(chain(latest_stable.keys(), latest_unstable.keys()))

        def stable_or_unstable_releases(ver):
            _last_stable_ver = latest_stable.get(ver, None)
            _last_unstable_ver = latest_unstable.get(ver, None)
            if _last_stable_ver and _last_unstable_ver:
                try:
                    if parse_version(_last_stable_ver.version) >= parse_version(_last_unstable_ver.version):
                        _last_unstable_ver = None
                except InvalidVersion:
                    pass
            return ver, {"stable": _last_stable_ver, "unstable": _last_unstable_ver}

        result = dict(map(stable_or_unstable_releases, all_versions))
        return {k: result[k] for k in result if any(list(result[k].values()))}

    def compatible_releases(self, platform_version, inclusive=True):
        """Returns all stable releases of this app that are compatible
        with the given platform version.

        :param inclusive: Use inclusive version check (see
                          AppRelease.is_compatible()).
        :return a sorted list of all compatible stable releases.
        """

        return sorted(
            filter(lambda r: r.is_compatible(platform_version, inclusive) and not r.is_unstable, self.releases.all()),
            key=lambda r: AppSemVer(r.version, r.is_nightly, r.last_modified),
            reverse=True,
        )

    def compatible_unstable_releases(self, platform_version, inclusive=True):
        """Returns all unstable releases of this app that are compatible with
        the given platform version.

        :param inclusive: Use inclusive version check (see
                          AppRelease.is_compatible()).
        :return a sorted list of all compatible unstable releases.
        """

        return sorted(
            filter(lambda r: r.is_compatible(platform_version, inclusive) and r.is_unstable, self.releases.all()),
            key=lambda r: AppSemVer(r.version, r.is_nightly, r.last_modified),
            reverse=True,
        )

    def is_outdated(self):
        """Checks if an app has been released in last 3 recent platform versions

        :return: True if not compatible, otherwise false
        """

        release_versions = list(self.latest_releases_by_platform_v().keys())
        if not release_versions:
            return True
        max_release_version = max(map(lambda v: Version(pad_max_inc_version(v)), release_versions))
        min_recent_version = Version(pad_min_version("27"))  # current Nextcloud version - 2
        return max_release_version < min_recent_version

    def _latest(self, releases):
        try:
            return max(releases, key=lambda r: AppSemVer(r.version, r.is_nightly, r.last_modified))
        except ValueError:
            return None

    def save(self, *args, **kwargs):
        # If the certificate has changed, delete all releases.
        try:
            if self.pk is not None:
                orig = App.objects.get(pk=self.pk)
                current = self.certificate.replace("\r", "").strip()
                former = orig.certificate.replace("\r", "").strip()
                # for some reason the django admin inserts \r\n for \n so
                # saving a model in the admin with the same cert kills all
                # releases
                if current != former:
                    self.releases.all().delete()
        except self.DoesNotExist:
            pass
        super().save(*args, **kwargs)


class AppRating(TranslatableModel):
    app = ForeignKey("App", related_name="ratings", verbose_name=_("App"), on_delete=CASCADE)
    user = ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=CASCADE, related_name="app_ratings")
    rating = FloatField(verbose_name=_("Rating"), default=0.5, help_text=_("Rating from 0.0 (worst) to 1.0 (best)"))
    rated_at = DateTimeField(db_index=True, auto_now_add=True)
    last_modified = DateTimeField(db_index=True, auto_now=True)
    translations = TranslatedFields(
        comment=TextField(
            verbose_name=_("Rating comment"), default="", help_text=_("Rating comment in Markdown"), blank=True
        )
    )
    appeal = BooleanField(default=False, verbose_name=_("Appeal"))

    class Meta:
        unique_together = (("app", "user"),)
        verbose_name = _("App rating")
        verbose_name_plural = _("App ratings")
        ordering = ("-rated_at",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.rating)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update rating on the app
        app = self.app
        day_range = settings.RATING_RECENT_DAY_RANGE
        threshold = settings.RATING_THRESHOLD
        rating, num = self._compute_app_rating(day_range, threshold)
        app.rating_recent = rating
        app.rating_num_recent = num
        rating, num = self._compute_app_rating(threshold=threshold)
        app.rating_overall = rating
        app.rating_num_overall = num
        app.save()

    def _compute_app_rating(self, days: int = -1, threshold: int = 5) -> tuple[float, int]:
        """
        Computes an app rating based on
        :param days: passing 30 will only consider ratings from the last
        30 days,
         pass a negative number to include all ratings
        :param threshold: if the amount of ratings is lower than this
        number
        return 0.5
        :return: the app rating
        """
        app_ratings = AppRating.objects.filter(app=self.app)
        if days >= 0:
            range = timezone.now() - datetime.timedelta(days=days)
            app_ratings = app_ratings.filter(rated_at__gte=range)
        ratings = map(lambda r: r.rating, app_ratings)
        return compute_rating(list(ratings), threshold)


class AppAuthor(Model):
    name = CharField(max_length=256, verbose_name=_("Full name"))
    homepage = URLField(max_length=256, blank=True, verbose_name=_("Homepage"))
    mail = EmailField(max_length=256, verbose_name=_("Email"), blank=True)

    def __str__(self) -> str:
        if self.mail:
            mail = f"<{self.mail}>"
        else:
            mail = ""
        return f"{self.name} {mail}"

    class Meta:
        verbose_name = _("App author")
        verbose_name_plural = _("App authors")


class AppRelease(TranslatableModel):
    version = CharField(max_length=256, verbose_name=_("Version"), help_text=_("Version follows Semantic Versioning"))
    app = ForeignKey("App", on_delete=CASCADE, verbose_name=_("App"), related_name="releases")
    # dependencies
    php_extensions = ManyToManyField(
        "PhpExtension", blank=True, through="PhpExtensionDependency", verbose_name=_("PHP extension dependency")
    )
    databases = ManyToManyField(
        "Database", blank=True, through="DatabaseDependency", verbose_name=_("Database dependency")
    )
    licenses = ManyToManyField("License", verbose_name=_("License"))
    shell_commands = ManyToManyField("ShellCommand", blank=True, verbose_name=_("Shell command dependency"))
    php_version_spec = CharField(max_length=256, verbose_name=_("PHP version requirement"))
    platform_version_spec = CharField(max_length=256, verbose_name=_("Platform version requirement"))
    raw_php_version_spec = CharField(max_length=256, verbose_name=_("PHP version requirement (raw)"))
    raw_platform_version_spec = CharField(max_length=256, verbose_name=_("Platform version requirement (raw)"))
    min_int_size = IntegerField(
        blank=True, default=32, verbose_name=_("Minimum Integer bits"), help_text=_("e.g. 32 for 32-bit Integers")
    )
    download = URLField(max_length=256, blank=True, verbose_name=_("Archive download URL"))
    created = DateTimeField(auto_now_add=True, editable=False, verbose_name=_("Created at"))
    last_modified = DateTimeField(auto_now=True, editable=False, db_index=True, verbose_name=_("Updated at"))
    signature = TextField(verbose_name=_("Signature"), help_text=_("A signature using the app's certificate"))
    signature_digest = CharField(max_length=256, verbose_name=_("Signature hashing algorithm"))
    translations = TranslatedFields(
        changelog=TextField(
            verbose_name=_("Changelog"), help_text=_("The release changelog. Can contain Markdown"), default=""
        )
    )
    is_nightly = BooleanField(verbose_name=_("Nightly"), default=False)
    aa_is_system = BooleanField(
        verbose_name=_("AppAPI system app flag"),
        help_text=_(
            "Whether the application is system-wide (i.e. can impersonate the user without him interacting with the "
            "application)"
        ),
        null=True,
        default=None,
    )

    class Meta:
        verbose_name = _("App release")
        verbose_name_plural = _("App releases")
        unique_together = (("app", "version", "is_nightly"),)
        ordering = ["-version"]

    def can_update(self, user: User) -> bool:
        return self.app.owner == user or user in self.app.co_maintainers.all()

    def can_delete(self, user: User) -> bool:
        return self.can_update(user)

    def __str__(self) -> str:
        return f"{self.app} {self.version}"

    def is_compatible(self, platform_version, inclusive=False):
        """Checks if a release is compatible with a platform version

        :param platform_version: the platform version, not required to be
                                 semver compatible
        :param inclusive: if True the check will also return True if an app
                          requires 9.0.1 and the given platform version is 9.0
        :return: True if compatible, otherwise false
        """

        min_version = Version(pad_min_version(platform_version))
        spec = Spec(self.platform_version_spec)
        if inclusive:
            max_version = Version(pad_max_inc_version(platform_version))
            return min_version in spec or max_version in spec
        else:
            return min_version in spec

    @property
    def is_unstable(self):
        return (
            self.is_nightly
            or "-dev" in self.version
            or "-a" in self.version
            or "-alpha" in self.version
            or "-b" in self.version
            or "-beta" in self.version
            or "-rc" in self.version
            or "-RC" in self.version
        )


class AppApiReleaseDeployMethod(Model):
    app_release = ForeignKey(
        "AppRelease",
        on_delete=CASCADE,
        verbose_name=_("App release"),
        related_name="deploy_methods",
        db_index=True,
    )
    install_type = CharField(max_length=64, verbose_name=_("Deploy Identifier"))
    install_data = CharField(
        max_length=1024,
        verbose_name=_("Installer specific data"),
        help_text=_("JSON data for AppAPI installer depending on installation type"),
    )

    class Meta:
        db_table = "core_appapi_release_deploy_method"
        verbose_name = _("AppAPI release Deploy method")
        verbose_name_plural = _("AppAPI release Deploy methods")


class AppApiReleaseApiScope(Model):
    app_release = ForeignKey(
        "AppRelease",
        on_delete=CASCADE,
        verbose_name=_("App release"),
        related_name="api_scopes",
        db_index=True,
    )
    scope_name = CharField(max_length=32, verbose_name=_("Name of the API scope"))

    class Meta:
        db_table = "core_appapi_release_api_scopes"
        verbose_name = _("AppAPI release API Scope")
        verbose_name_plural = _("AppAPI release API Scopes")


class Screenshot(Model):
    url = URLField(max_length=256, verbose_name=_("Image URL"))
    small_thumbnail = URLField(max_length=256, verbose_name=_("Small thumbnail"), default="")
    app = ForeignKey("App", on_delete=CASCADE, verbose_name=_("App"), related_name="screenshots")
    ordering = IntegerField(verbose_name=_("Ordering"))

    class Meta:
        verbose_name = _("Screenshot")
        verbose_name_plural = _("Screenshots")
        ordering = ["ordering"]

    @property
    def front_img_small(self):
        if self.small_thumbnail:
            return self.small_thumbnail
        else:
            return self.url

    def __str__(self) -> str:
        return self.url


class ShellCommand(Model):
    name = CharField(
        max_length=256,
        unique=True,
        primary_key=True,
        verbose_name=_("Shell command"),
        help_text=_("Name of a required shell command, e.g. grep"),
    )

    class Meta:
        verbose_name = _("Shell command")
        verbose_name_plural = _("Shell commands")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Category(TranslatableModel):
    id = CharField(
        max_length=256,
        unique=True,
        primary_key=True,
        verbose_name=_("Id"),
        help_text=_("Category ID used to identify the category an app is uploaded to"),
    )
    created = DateTimeField(auto_now_add=True, editable=False, verbose_name=_("Created at"))
    last_modified = DateTimeField(auto_now=True, editable=False, db_index=True, verbose_name=_("Updated at"))
    translations = TranslatedFields(
        name=CharField(
            max_length=256, help_text=_("Category name which will be presented to the user"), verbose_name=_("Name")
        ),
        description=TextField(verbose_name=_("Description"), help_text=_("Will be rendered as Markdown")),
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name


class License(Model):
    id = CharField(
        max_length=256,
        unique=True,
        primary_key=True,
        verbose_name=_("Id"),
        help_text=_("Key which is used to identify a license"),
    )
    name = CharField(
        max_length=256, verbose_name=_("Name"), help_text=_("License name which will be presented to the user")
    )

    class Meta:
        verbose_name = _("License")
        verbose_name_plural = _("Licenses")

    def __str__(self) -> str:
        return self.name


class Database(Model):
    id = CharField(
        max_length=256,
        unique=True,
        primary_key=True,
        verbose_name=_("Id"),
        help_text=_("Key which is used to identify a database"),
    )
    name = CharField(
        max_length=256, verbose_name=_("Name"), help_text=_("Database name which will be presented to the user")
    )

    class Meta:
        verbose_name = _("Database")
        verbose_name_plural = _("Databases")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class DatabaseDependency(Model):
    app_release = ForeignKey(
        "AppRelease", on_delete=CASCADE, verbose_name=_("App release"), related_name="databasedependencies"
    )
    database = ForeignKey("Database", related_name="releasedependencies", on_delete=CASCADE, verbose_name=_("Database"))
    version_spec = CharField(max_length=256, verbose_name=_("Database version requirement"))
    raw_version_spec = CharField(max_length=256, verbose_name=_("Database version requirement (raw)"))

    class Meta:
        verbose_name = _("Database dependency")
        verbose_name_plural = _("Database dependencies")
        unique_together = (("app_release", "database", "version_spec"),)

    def __str__(self) -> str:
        return f"{self.app_release}: {self.database} {self.version_spec}"


class PhpExtension(Model):
    id = CharField(
        max_length=256, unique=True, help_text=_("e.g. libxml"), primary_key=True, verbose_name=_("PHP extension")
    )

    class Meta:
        verbose_name = _("PHP extension")
        verbose_name_plural = _("PHP extensions")
        ordering = ["id"]

    def __str__(self) -> str:
        return self.id


class PhpExtensionDependency(Model):
    app_release = ForeignKey(
        "AppRelease", on_delete=CASCADE, verbose_name=_("App release"), related_name="phpextensiondependencies"
    )
    php_extension = ForeignKey(
        "PhpExtension", on_delete=CASCADE, verbose_name=_("PHP extension"), related_name="releasedependencies"
    )
    version_spec = CharField(max_length=256, verbose_name=_("Extension version requirement"))
    raw_version_spec = CharField(max_length=256, verbose_name=_("Extension version requirement (raw)"))

    class Meta:
        verbose_name = _("PHP extension dependency")
        verbose_name_plural = _("PHP extension dependencies")
        unique_together = (("app_release", "php_extension", "version_spec"),)

    def __str__(self) -> str:
        return f"{self.app_release.app}: {self.php_extension} {self.version_spec}"


class Podcast(Model):
    title = CharField(max_length=256, verbose_name=_("Heading"))
    excerpt = CharField(max_length=512, verbose_name=_("Excerpt"))
    link = CharField(max_length=256, unique=True, verbose_name=_("Link"))
    image = CharField(max_length=256, verbose_name=_("Image"))
    show = BooleanField(verbose_name=_("Show podcast"), default=True)

    class Meta:
        verbose_name = _("Nextcloud Podcast")
        verbose_name_plural = _("Nextcloud Podcasts")

    def __str__(self):
        return f"{self.title} ({self.link})"


@receiver(post_delete, sender=App)
def record_app_delete(sender, **kwargs):
    AppReleaseDeleteLog.objects.create()


@receiver(post_delete, sender=AppRelease)
def record_app_release_delete(sender, **kwargs):
    AppReleaseDeleteLog.objects.create()


class AppReleaseDeleteLog(Model):
    """
    Used to keep track of app and app release deletions
    """

    last_modified = DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = _("App release deletion")
        verbose_name_plural = _("App release deletions")

    def __str__(self) -> str:
        return str(self.last_modified)


@receiver(post_delete, sender=AppRating)
def record_app_rating_delete(sender, **kwargs):
    AppRatingDeleteLog.objects.create()


class AppRatingDeleteLog(Model):
    """
    Used to keep track of app rating deletions
    """

    last_modified = DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = _("App rating deletion")
        verbose_name_plural = _("App rating deletions")

    def __str__(self) -> str:
        return str(self.last_modified)


class NextcloudReleaseManager(Manager):
    pass


class NextcloudRelease(Model):
    objects = NextcloudReleaseManager()
    version = CharField(
        max_length=100, verbose_name=_("Nextcloud version"), help_text=_("e.g. 9.0.54"), primary_key=True
    )
    is_current = BooleanField(
        verbose_name=_("Is current version"),
        help_text=_(
            "Only one version can be "
            "the current one. This field is "
            "used to pre-select dropdowns for "
            "app generation, etc."
        ),
        default=False,
    )
    has_release = BooleanField(
        verbose_name=_("Has a release"),
        help_text=_(
            "If true, this is an actual released "
            "Nextcloud version that can be "
            "downloaded as an archive. If false, "
            "the release is either a pre-release, "
            "or not available for download "
            "anymore."
        ),
        default=False,
    )
    is_supported = BooleanField(
        verbose_name=_("Version is supported"),
        help_text=_("True if this version is still officially supported (excluding enterprise support)"),
        default=False,
    )

    class Meta:
        verbose_name = _("Nextcloud release")
        verbose_name_plural = _("Nextcloud releases")
        ordering = ("-version",)

    def __str__(self):
        return self.version
