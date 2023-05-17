import csv
from datetime import datetime

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.views.generic import FormView

from nextcloudappstore.core.models import App, NextcloudRelease, Screenshot
from nextcloudappstore.scaffolding.archive import build_archive
from nextcloudappstore.scaffolding.forms import (
    AppScaffoldingForm,
    IntegrationScaffoldingForm,
)


class AppScaffoldingView(FormView):
    template_name = "app/scaffold.html"
    form_class = AppScaffoldingForm

    def get_initial(self):
        init = {"platform": NextcloudRelease.get_current_main(), "categories": ("tools",)}
        if self.request.user.is_authenticated:
            user = self.request.user
            init["author_name"] = "%s %s" % (user.first_name, user.last_name)
            init["author_email"] = user.email
        return init

    def form_valid(self, form):
        if settings.APP_SCAFFOLDING_LOG:
            with open(settings.APP_SCAFFOLDING_LOG, "a") as csvfile:
                data = form.cleaned_data
                entries = data.values() if ["opt_in"] else [data["name"]]
                logwriter = csv.writer(csvfile, delimiter="|")
                logwriter.writerow([datetime.now(), *entries])
        buffer = build_archive(form.cleaned_data)
        response = HttpResponse(content_type="application/tar+gzip")
        response["Content-Disposition"] = 'attachment; filename="app.tar.gz"'
        value = buffer.getvalue()
        buffer.close()
        response.write(value)
        return response


class IntegrationScaffoldingView(LoginRequiredMixin, FormView):
    template_name = "app/integration_scaffold.html"
    form_class = IntegrationScaffoldingForm
    success_url = "/"
    app_id = None

    def get(self, request, *args, **kwargs):
        self.app_id = self.kwargs.get("pk", None)
        if self.app_id is not None:
            app = App.objects.get(id=self.app_id)
            if not app.approved and not request.user.is_superuser:
                raise Http404("Not found")

        return self.render_to_response(self.get_context_data())

    def get_initial(self):
        init = {"categories": ("integration",)}

        if self.app_id is not None:
            app = App.objects.get(id=self.app_id)
            screenshots = Screenshot.objects.filter(app=app)
            if len(screenshots) == 1:
                screenshot = screenshots[0]
                init["screenshot"] = screenshot.url
                init["screenshot_thumbnail"] = screenshot.small_thumbnail
            init["description"] = app.description
            init["name"] = app.name
            init["summary"] = app.summary
            init["author_homepage"] = app.website
            init["issue_tracker"] = app.issue_tracker

        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.app_id is None:
            context["integration_page"] = "developer-integration"
        else:
            app = App.objects.get(id=self.app_id)
            if not app.approved:
                context["integration_page"] = "account-integration-moderate"
            else:
                context["integration_page"] = "account-integration"

        return context

    def form_valid(self, form):
        action = "save"
        if self.request.method == "POST":
            if "reject" in self.request.POST:
                action = "reject"
            elif "approve" in self.request.POST:
                action = "approve"

        return_value = form.save(self.request.user, self.app_id, action)
        self.success_url = "/apps/{}".format(return_value)

        if action != "save":
            self.success_url = reverse("user:account-integrations")
        elif return_value is None:
            self.success_url = "/"

        return super().form_valid(form)
