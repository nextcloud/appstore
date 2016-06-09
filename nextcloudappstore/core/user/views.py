from django.shortcuts import render

import registration.backends.simple.views 

from nextcloudappstore.core.user.forms import RegistrationFormRecaptcha
class RegistrationView(registration.backends.simple.views.RegistrationView):
    
    form_class = RegistrationFormRecaptcha

    def get_success_url(self, user):
        return u'/'