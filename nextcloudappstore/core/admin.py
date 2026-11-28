"""
SPDX-FileCopyrightText: 2016 Nextcloud GmbH and Nextcloud contributors
SPDX-License-Identifier: AGPL-3.0-or-later
"""

import datetime

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _  # type: ignore
from parler.admin import TranslatableAdmin

from nextcloudappstore.certificate.validator import certificate_info
from nextcloudappstore.core.forms import CertificateRenewalForm
from nextcloudappstore.core.models import (
    App,
    AppApiEnvironmentVariable,
    AppApiReleaseApiScope,
    AppApiReleaseDeployMethod,
    AppAuthor,
    AppRating,
    AppRelease,
    AppReleaseDeleteLog,
    Category,
    Database,
    DatabaseDependency,
    Donation,
    License,
    NextcloudRelease,
    PhpExtension,
    PhpExtensionDependency,
    Podcast,
    Screenshot,
    ShellCommand,
    Video,
)


class DatabaseDependencyInline(admin.TabularInline):
    model = DatabaseDependency
    extra = 1


class PhpExtensionDependencyInline(admin.TabularInline):
    model = PhpExtensionDependency
    extra = 1


@admin.register(AppReleaseDeleteLog)
class AppReleaseAdmin(admin.ModelAdmin):
    list_display = ("last_modified",)
    list_filter = ("last_modified",)
    ordering = ("-last_modified",)


@admin.register(AppRelease)
class AppReleaseAdmin(TranslatableAdmin):  # noqa
    inlines = (DatabaseDependencyInline, PhpExtensionDependencyInline)
    list_display = ("app", "version", "is_nightly", "last_modified", "release_date")
    list_filter = ("app__id", "is_nightly", "last_modified")
    ordering = ("-last_modified",)
    readonly_fields = ("signature_digest",)


@admin.register(AppAuthor)
class AppAuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "mail", "homepage")


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("id", "name")


CERTIFICATE_EXPIRY_WARNING = datetime.timedelta(days=60)


class CertificateExpiryFilter(admin.SimpleListFilter):
    title = _("certificate")
    parameter_name = "certificate_expiry"

    def lookups(self, request, model_admin):
        return (
            ("soon", _("Expires within 60 days")),
            ("expired", _("Expired")),
        )

    def queryset(self, request, queryset):
        if self.value() not in ("soon", "expired"):
            return queryset
        now = timezone.now()
        ids = []
        for app_id, certificate in queryset.values_list("id", "certificate"):
            try:
                expires = certificate_info(certificate)["expires"]
            except ValueError:
                continue
            if expires < now if self.value() == "expired" else now <= expires < now + CERTIFICATE_EXPIRY_WARNING:
                ids.append(app_id)
        return queryset.filter(id__in=ids)


@admin.register(App)
class AppAdmin(TranslatableAdmin):
    list_display = (
        "id",
        "owner",
        "certificate_expiry",
        "name",
        "last_release",
        "release_date",
        "rating_recent",
        "rating_overall",
        "summary",
        "is_featured",
        "ownership_transfer_enabled",
        "is_orphan",
        "is_deprecated",
        "is_integration",
        "is_enterprise_supported",
        "is_enterprise_only",
        "approved",
    )
    list_filter = (
        CertificateExpiryFilter,
        "owner",
        "co_maintainers",
        "categories",
        "created",
        "is_featured",
        "last_release",
        "ownership_transfer_enabled",
        "is_orphan",
        "is_deprecated",
        "is_integration",
        "is_enterprise_supported",
        "is_enterprise_only",
        "approved",
    )
    ordering = ("id",)

    @admin.display(description=_("Certificate expires"))
    def certificate_expiry(self, obj):
        try:
            expires = certificate_info(obj.certificate)["expires"]
        except ValueError:
            return "-"
        if expires - timezone.now() < CERTIFICATE_EXPIRY_WARNING:
            return format_html('<span class="certificate-expiry-warning">{}</span>', expires.date().isoformat())
        return expires.date().isoformat()

    @admin.display(description=_("Certificate expires"))
    def certificate_renewal(self, obj):
        expiry = self.certificate_expiry(obj)
        if expiry == "-":
            return expiry
        return format_html(
            '{}<a class="button certificate-renew-button" href="{}">{}</a>',
            expiry,
            reverse("admin:core_app_renew_certificate", args=[obj.pk]),
            _("Renew certificate"),
        )

    def get_readonly_fields(self, request, obj=None):
        # Existing certificates are only replaced through the renewal page.
        if obj is not None:
            return (*super().get_readonly_fields(request, obj), "certificate", "certificate_renewal")
        return super().get_readonly_fields(request, obj)

    def get_urls(self):
        return [
            path(
                "<path:object_id>/renew-certificate/",
                self.admin_site.admin_view(self.renew_certificate_view),
                name="core_app_renew_certificate",
            ),
            *super().get_urls(),
        ]

    def renew_certificate_view(self, request, object_id):
        app = get_object_or_404(App, pk=object_id)
        if not self.has_change_permission(request, app):
            raise PermissionDenied

        form = CertificateRenewalForm(request.POST or None, app=app)
        if request.method == "POST" and form.is_valid():
            app.certificate = form.cleaned_data["certificate"]
            app.save()
            messages.success(request, _("The certificate was renewed. All releases were kept."))
            return redirect(reverse("admin:core_app_change", args=[app.pk]))

        try:
            current = certificate_info(app.certificate)
        except ValueError:
            current = None
        context = {
            **self.admin_site.each_context(request),
            "title": _("Renew certificate: %(app)s") % {"app": app.id},
            "opts": self.model._meta,
            "original": app,
            "form": form,
            "current": current,
            "expiry": self.certificate_expiry(app),
        }
        return TemplateResponse(request, "admin/core/app/renew_certificate.html", context)


@admin.register(AppRating)
class AppRatingAdmin(TranslatableAdmin):
    list_display = ("rating", "app", "user", "rated_at", "last_modified")
    list_filter = ("app__id", "user", "rating", "rated_at", "last_modified")


@admin.register(Database)
class DatabaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(DatabaseDependency)
class DatabaseDependencyAdmin(admin.ModelAdmin):
    list_display = ("app_release", "database", "version_spec")
    list_filter = ("app_release", "database")


@admin.register(PhpExtension)
class PhpExtensionAdmin(admin.ModelAdmin):
    pass


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(PhpExtensionDependency)
class PhpExtensionDependencyAdmin(admin.ModelAdmin):
    list_display = ("app_release", "php_extension", "version_spec")
    list_filter = ("app_release", "php_extension")


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ("title", "excerpt", "link", "image")


@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
    ordering = ("app", "ordering")
    list_display = ("url", "small_thumbnail", "app", "ordering")
    list_filter = ("app__id",)


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    ordering = ("app", "ordering")
    list_display = ("url", "app", "ordering")
    list_filter = ("app__id",)


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    ordering = ("app", "ordering")
    list_display = ("url", "type", "title", "app", "ordering")
    list_filter = ("app__id",)


@admin.register(NextcloudRelease)
class NextcloudReleaseAdmin(admin.ModelAdmin):
    list_display = ("version", "is_current", "has_release", "is_supported")
    list_filter = ("is_current", "has_release", "is_supported")


@admin.register(ShellCommand)
class ShellCommandAdmin(admin.ModelAdmin):
    pass


@admin.register(AppApiReleaseApiScope)
class AppApiReleaseApiScopeAdmin(admin.ModelAdmin):
    pass


@admin.register(AppApiReleaseDeployMethod)
class AppApiReleaseDeployMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(AppApiEnvironmentVariable)
class AppApiEnvironmentVariable(admin.ModelAdmin):
    pass
