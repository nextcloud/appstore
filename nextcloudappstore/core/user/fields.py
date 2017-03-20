from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import CharField
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UsernameField(CharField):

    def to_python(self, value):
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist:
            raise ValidationError(_('There is no such user.'), code='no-user')
