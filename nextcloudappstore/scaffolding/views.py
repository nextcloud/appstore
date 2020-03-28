from django.http import HttpResponse
from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from nextcloudappstore.core.models import App, Screenshot, NextcloudRelease
from nextcloudappstore.scaffolding.archive import build_archive
from nextcloudappstore.scaffolding.forms import AppScaffoldingForm, \
    IntegrationScaffoldingForm


class AppScaffoldingView(FormView):
    template_name = 'app/scaffold.html'
    form_class = AppScaffoldingForm

    def get_initial(self):
        init = {
            'platform': NextcloudRelease.get_current_main(),
            'categories': ('tools',)
        }
        if self.request.user.is_authenticated:
            user = self.request.user
            init['author_name'] = '%s %s' % (user.first_name, user.last_name)
            init['author_email'] = user.email
        return init

    def form_valid(self, form):
        buffer = build_archive(form.cleaned_data)
        response = HttpResponse(content_type='application/tar+gzip')
        response['Content-Disposition'] = 'attachment; filename="app.tar.gz"'
        value = buffer.getvalue()
        buffer.close()
        response.write(value)
        return response


class IntegrationScaffoldingView(LoginRequiredMixin, FormView):
    template_name = 'app/integration_scaffold.html'
    form_class = IntegrationScaffoldingForm
    success_url = '/'
    app_id = None

    def get_initial(self):
        self.app_id = self.kwargs.get('pk', None)

        init = {
            'categories': ('integration',)
        }

        if self.app_id is not None:
            app = App.objects.get(id=self.app_id)
            screenshots = Screenshot.objects.filter(app=app)
            if len(screenshots) == 1:
                screenshot = screenshots[0]
                init['screenshot'] = screenshot.url
                init['screenshot_thumbnail'] = screenshot.small_thumbnail
            init['description'] = app.description
            init['name'] = app.name
            init['summary'] = app.summary
            init['author_homepage'] = app.website
            init['issue_tracker'] = app.issue_tracker

        user = self.request.user
        init['author_name'] = '%s %s' % (user.first_name, user.last_name)
        init['author_email'] = user.email

        return init

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.app_id is None:
            context['integration_page'] = 'developer-integration'
        else:
            context['integration_page'] = 'account-integration'

        return context

    def form_valid(self, form):
        self.success_url = form.save(self.request.user, self.app_id)
        return super().form_valid(form)

    def get_success_url(self):
        return "/apps/{}".format(self.success_url)
