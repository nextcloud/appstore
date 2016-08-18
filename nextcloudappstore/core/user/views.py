from allauth.account.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.utils.translation import get_language_info, get_language
from django.views.generic import TemplateView, UpdateView
from django.views.generic.list import ListView
from nextcloudappstore.core.models import App
from django.contrib import messages
from rest_framework.authtoken.models import Token


class AccountView(LoginRequiredMixin, UpdateView):
    """Display and allow changing of the user's name."""
    template_name = 'user/account.html'
    template_name_suffix = ''
    model = User
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('user-account')

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        context['acc_page'] = 'account'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Name saved.')
        return super(AccountView, self).form_valid(form)

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated():
            return self.request.user
        else:
            return None


class MyAppsView(LoginRequiredMixin, ListView):
    """List the user's apps."""
    template_name = 'user/my_apps.html'
    model = App

    def get_context_data(self, **kwargs):
        context = super(MyAppsView, self).get_context_data(**kwargs)
        context['acc_page'] = 'my_apps'
        return context

    def get_queryset(self):
        lang = get_language_info(get_language())['code']
        qs = App.objects.search('', lang).order_by('translations__name')
        return qs.filter(
            Q(owner=self.request.user) | Q(co_maintainers=self.request.user))


class APITokenView(LoginRequiredMixin, TemplateView):
    """Display the user's API Token."""
    template_name = 'user/api_token.html'

    def get_context_data(self, **kwargs):
        context = super(APITokenView, self).get_context_data(**kwargs)
        context['acc_page'] = 'api_token'
        if self.request.user.is_authenticated():
            token = Token.objects.get_or_create(user=self.request.user)[0].key
        else:
            token = ''
        context['token'] = token
        return context

    def post(self, request):
        if self.request.user.is_authenticated():
            try:
                Token.objects.get(user=self.request.user).delete()
            except:
                pass
            new = Token.objects.create(user=self.request.user)
            new.save()
            messages.success(request, 'New API token generated.')
        return self.get(request)


class PasswordView(LoginRequiredMixin, PasswordChangeView):
    """Allow the user to change their password."""
    template_name = 'user/password.html'
    success_url = reverse_lazy('user-password')

    def get_context_data(self, **kwargs):
        context = super(PasswordView, self).get_context_data(**kwargs)
        context['acc_page'] = 'password'
        return context
