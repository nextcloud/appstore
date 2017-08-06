from django.http import HttpResponse
from django.views.generic import FormView

from nextcloudappstore.core.models import NextcloudRelease
from nextcloudappstore.scaffolding.archive import build_archive
from nextcloudappstore.scaffolding.forms import AppScaffoldingForm


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
