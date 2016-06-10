from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from registration.backends.simple.views \
     import RegistrationView as BaseRegistrationView

from nextcloudappstore.core.user.forms import RegistrationFormRecaptcha


class RegistrationView(BaseRegistrationView):

    form_class = RegistrationFormRecaptcha

    def get_success_url(self, user):
        return reverse('home')

    def register(self, form):
        super().register(form)
        messages.add_message(self.request, messages.SUCCESS,
                             _("Thank you for registering!"))
