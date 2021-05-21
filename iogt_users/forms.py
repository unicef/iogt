from allauth.utils import set_form_field_order
from allauth.account.forms import SignupForm, PasswordField
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import TextInput
from wagtail.users.forms import UserEditForm as WagtailUserEditForm, UserCreationForm as WagtailUserCreationForm, \
    custom_fields, standard_fields

from .models import User
from .utils import get_wagtail_admin_user_standard_fields


class AccountSignupForm(SignupForm):
    display_name = forms.CharField(label='Display Name', required=False, max_length=150)
    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')

    field_order = [
        "username",
        "password1",
        "password2",
        "display_name",
        "email",
        "terms_accepted"
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
        model = User
        fields = ('username',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'groups', 'user_permissions')


class WagtailAdminUserCreateForm(WagtailUserCreationForm):
    email = forms.EmailField(required=False, label='Email')
    first_name = None
    last_name = None
    display_name = forms.CharField(label='Display Name', required=False, max_length=150)
    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')

    class Meta(WagtailUserCreationForm.Meta):
        fields = set([User.USERNAME_FIELD]) | get_wagtail_admin_user_standard_fields() | custom_fields


class WagtailAdminUserEditForm(WagtailUserEditForm):
    email = forms.EmailField(required=False, label='Email')
    first_name = None
    last_name = None
    display_name = forms.CharField(label='Display Name', required=False, max_length=150)
    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')

    class Meta(WagtailUserEditForm.Meta):
        fields = set([User.USERNAME_FIELD, "is_active"]) | get_wagtail_admin_user_standard_fields() | custom_fields
