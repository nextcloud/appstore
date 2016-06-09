from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import ugettext as _

import registration.backends.simple.views 

from nextcloudappstore.core.user.forms import RegistrationFormRecaptcha


class RegistrationView(registration.backends.simple.views.RegistrationView):
    
    form_class = RegistrationFormRecaptcha

    def get_success_url(self, user):
        return u'/'
    
    def register(self, form):
        super().register(form)
        messages.add_message(self.request, messages.SUCCESS,_("Thank you for registering!"))