from allauth.account.forms import SignupForm, PasswordField
from allauth.utils import set_form_field_order
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import TextInput, Field
from wagtail.users.forms import UserEditForm as WagtailUserEditForm, \
    UserCreationForm as WagtailUserCreationForm

from .models import User


class AccountSignupForm(SignupForm):
    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')

    field_order = [
        "username",
        "password1",
        "password2",
        "terms_accepted",
        "display_name"
    ]

    def __init__(self, *args, **kwargs):
        super(AccountSignupForm, self).__init__(*args, **kwargs)
        self.fields.pop('email')
        self.fields["password1"] = PasswordField(
            label="4-digit PIN", autocomplete="new-password", max_length=4,
            widget=TextInput(attrs={'type': 'number'})
        )
        self.fields["display_name"] = Field(
            widget=TextInput(
                attrs={'type': 'text', "placeholder": "Enter Your Name"})
        )

        if 'password2' in self.fields:
            self.fields["password2"] = PasswordField(
                label="Confirm 4-digit PIN", max_length=4,
                widget=TextInput(attrs={'type': 'number'}))

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'groups', 'user_permissions')


class WagtailAdminUserCreateForm(WagtailUserCreationForm):
    email = forms.EmailField(required=False, label='Email')
    first_name = forms.CharField(required=False, label='First Name')
    last_name = forms.CharField(required=False, label='Last Name')
    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')


class WagtailAdminUserEditForm(WagtailUserEditForm):
    email = forms.EmailField(required=False, label='Email')
    first_name = forms.CharField(required=False, label='First Name')
    last_name = forms.CharField(required=False, label='Last Name')

    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')
