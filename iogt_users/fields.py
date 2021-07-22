from allauth.account.forms import PasswordField
from django.forms import TextInput


class IogtPasswordField(PasswordField):

    def __init__(self, label, autocomplete, **kwargs):
        super().__init__(label=label, max_length=4, autocomplete=autocomplete,
                         widget=TextInput(attrs={'type': 'number'}), **kwargs)
