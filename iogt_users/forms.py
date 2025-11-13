from allauth.account.forms import SignupForm, ChangePasswordForm as BaseChangePasswordForm
from allauth.utils import set_form_field_order
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.users.forms import UserEditForm as WagtailUserEditForm, \
    UserCreationForm as WagtailUserCreationForm
from user_notifications.models import UserNotificationTemplate
from user_notifications.tasks import send_app_notifications

from .fields import IogtPasswordField
from .models import User

from notifications.signals import notify
from datetime import datetime


class UserFieldsMixin(forms.Form):
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        required=False
    )
    year = forms.TypedChoiceField(
        choices=[('', 'Select Year')] + [(y, y) for y in range(1950, datetime.now().year)],
        coerce=int,
        empty_value=None,
        required=False
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'location' in self.fields:
            self.fields['location'].widget = forms.TextInput(attrs={
                "placeholder": _("Current location")
            })

class AccountSignupForm(UserFieldsMixin, SignupForm):
    display_name = forms.CharField(
        label=_("Display name"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Choose a display name that will be shown publicly if you post to the IoGT site, for example next to comments you post"),}
        ),
        required=False,
    )
    year = forms.TypedChoiceField(
            choices=[('', 'Select Year')] + [(year, year) for year in range(1950, datetime.now().year + 1)],
            coerce=int,
            empty_value=None,
            required=False,
        )
    gender = forms.ChoiceField(
        choices= [('', 'Select Gender'),("male", "Male"), ("female", "Female"), ("other", "Other")],
        required=False,
    )
    location = forms.CharField(
        required=False,
        max_length=255
    )
    terms_accepted = forms.BooleanField(label=_('I accept the Terms and Conditions.'))
    field_order = [
        "username",
        "display_name",
        "year",
        "gender",
        "location",
        "password1",
        "password2",
        "terms_accepted",
    ]

    def __init__(self, *args, **kwargs):
        super(AccountSignupForm, self).__init__(*args, **kwargs)
        self.fields.pop('email')
        self.fields["password1"] = IogtPasswordField(label=_("Choose a 4-digit PIN or a longer password that you will use to login to IoGT"), autocomplete="new-password")

        if 'password2' in self.fields:
            self.fields["password2"] = IogtPasswordField(label=_("Repeat your 4-digital PIN or longer password"), autocomplete="new-password")

        self.fields["username"].widget = forms.TextInput(attrs={
            "placeholder": _("Choose a username that you will use to login to IoGT")
        })

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def save(self, request):
        user = super().save(request)
        send_app_notifications.delay(user.id, notification_type='signup')
        user.year = self.cleaned_data["year"]
        user.gender = self.cleaned_data["gender"]
        user.location = self.cleaned_data["location"]
        user.save()
        return user

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
    class Meta(WagtailUserCreationForm.Meta):
        model = User
        fields = WagtailUserCreationForm.Meta.fields | {'first_name', 'last_name', 'username', 'display_name', 'terms_accepted', 'groups'}


class WagtailAdminUserEditForm(WagtailUserEditForm):
    email = forms.EmailField(required=False, label='Email')
    display_name = forms.CharField(required=False, label='Display Name')
    first_name = forms.CharField(required=False, label='First Name')
    last_name = forms.CharField(required=False, label='Last Name')

    terms_accepted = forms.BooleanField(label=_('I accept the Terms and Conditions.'))

    class Meta(WagtailUserEditForm.Meta):
        model = User
        fields = WagtailUserEditForm.Meta.fields | {'first_name', 'last_name', 'username', 'display_name', 'terms_accepted', 'groups'}