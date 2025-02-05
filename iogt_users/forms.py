from allauth.account.forms import SignupForm, ChangePasswordForm as BaseChangePasswordForm
from allauth.utils import set_form_field_order
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.users.forms import UserEditForm as WagtailUserEditForm, \
    UserCreationForm as WagtailUserCreationForm

from .fields import IogtPasswordField
from .models import User


class AccountSignupForm(SignupForm):
    display_name = forms.CharField(
        label=_("Display name"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Display name"),}
        ),
        required=False,
    )
    terms_accepted = forms.BooleanField(label=_('I accept the Terms and Conditions.'))

    field_order = [
        "username",
        "display_name",
        "password1",
        "password2",
        "terms_accepted",
    ]

    def __init__(self, *args, **kwargs):
        super(AccountSignupForm, self).__init__(*args, **kwargs)
        self.fields.pop('email')
        self.fields["password1"] = IogtPasswordField(label=_("4-digit PIN"), autocomplete="new-password")

        if 'password2' in self.fields:
            self.fields["password2"] = IogtPasswordField(label=_("4-digit PIN"), autocomplete="new-password")

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username):
            raise ValidationError(_('Username not available.'))
        return username

    def clean_displayname(self):
        display_name = self.cleaned_data.get('display_name')
        if User.objects.filter(display_name__iexact=display_name):
            raise ValidationError(_('Display name not available.'))
        return display_name


class ChangePasswordForm(BaseChangePasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["oldpassword"] = IogtPasswordField(label=_("Old 4-digit PIN"), autocomplete='old-password')
        self.fields["password1"] = IogtPasswordField(label=_("New 4-digit PIN"), autocomplete='old-password')
        self.fields["password2"] = IogtPasswordField(label=_("Confirm new 4-digit PIN"), autocomplete='old-password')


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'display_name',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'display_name', 'groups', 'user_permissions')


class WagtailAdminUserCreateForm(WagtailUserCreationForm):
    email = forms.EmailField(required=False, label='Email')
    display_name = forms.CharField(required=False, label='Display Name')
    first_name = forms.CharField(required=False, label='First Name')
    last_name = forms.CharField(required=False, label='Last Name')
    terms_accepted = forms.BooleanField(label=_('I accept the Terms and Conditions.'))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username):
            raise ValidationError(_('A user with that username already exists.'))
        return username

    def clean_displayname(self):
        display_name = self.cleaned_data.get('display_name')
        if User.objects.filter(display_name__iexact=display_name):
            raise ValidationError(_('Display name not available.'))
        return display_name


class WagtailAdminUserEditForm(WagtailUserEditForm):
    email = forms.EmailField(required=False, label='Email')
    display_name = forms.CharField(required=False, label='Display Name')
    first_name = forms.CharField(required=False, label='First Name')
    last_name = forms.CharField(required=False, label='Last Name')

    terms_accepted = forms.BooleanField(label=_('I accept the Terms and Conditions.'))
