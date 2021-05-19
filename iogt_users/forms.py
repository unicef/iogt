from allauth.utils import set_form_field_order
from allauth.account.forms import SignupForm, PasswordField
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import TextInput

from iogt_users.models import IogtUser


class AccountSignupForm(SignupForm):
    display_name = forms.CharField(label='Display Name', max_length=150)
    has_accepted_terms_and_conditions = forms.BooleanField(label='I accept the terms & conditions')

    field_order = [
        "username",
        "password1",
        "password2",
        "display_name",
        "email",
        "has_accepted_terms_and_conditions"
    ]

    def __init__(self, *args, **kwargs):
        super(AccountSignupForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = PasswordField(
            label="4-digit PIN", autocomplete="new-password", max_length=4, widget=TextInput(attrs={'type': 'number'})
        )

        if 'password2' in self.fields:
            self.fields["password2"] = PasswordField(label="Confirm 4-digit PIN", max_length=4,
                                                     widget=TextInput(attrs={'type': 'number'}))

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = IogtUser
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = IogtUser
        fields = ('username',)
