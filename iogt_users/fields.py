from allauth.account.forms import PasswordField
from django.forms import TextInput


class IogtPasswordField(PasswordField):

    def __init__(self, label, autocomplete, css_class='', **kwargs):
        super().__init__(label=label, max_length=4, autocomplete=autocomplete, **kwargs)
        self.widget.attrs.update({
            "class": css_class,
            "type": "number"
        })
