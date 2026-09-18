from allauth.account.forms import SignupForm, ChangePasswordForm as BaseChangePasswordForm
from allauth.utils import set_form_field_order
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from questionnaires.models import UserSubmission
from wagtail.users.forms import UserEditForm as WagtailUserEditForm, \
    UserCreationForm as WagtailUserCreationForm
from user_notifications.models import UserNotificationTemplate
from user_notifications.tasks import send_app_notifications

from .fields import IogtPasswordField
from .models import User

from notifications.signals import notify
from datetime import datetime

class AccountSignupForm(SignupForm):
    display_name = forms.CharField(
        label=_("Display name"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Choose a display name to be shown publicly"),
                "class": "signup-input",
            }
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
        self.fields["password1"] = IogtPasswordField(label=_("Choose 4-digit PIN or password"), autocomplete="new-password", css_class="signup-input")

        if 'password2' in self.fields:
            self.fields["password2"] = IogtPasswordField(label=_("Repeat 4-digital PIN or password"), autocomplete="new-password", css_class="signup-input")

        self.fields["username"].widget = forms.TextInput(attrs={
            "placeholder": _("Choose a username to log in to IoGT"),
            "class": "signup-input"
        })

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def save(self, request):
        user = super().save(request)
        send_app_notifications.delay(user.id, notification_type='signup')
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
    
    gender_edit = forms.CharField(required=False, label="Gender")
    date_of_birth_edit = forms.DateField(required=False, label="Date of Birth")
    location_edit = forms.CharField(required=False, label="Location")

    terms_accepted = forms.BooleanField(label=_('I accept the Terms and Conditions.'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.instance
        submission = None
        # PRE-FILL from latest UserSubmission
        submission  = UserSubmission.objects.filter(
            user_id=user.id,
            page__slug="registration-survey"
        ).order_by("-submit_time").first()
        if submission:
            data = submission.form_data or {}
            self.fields["gender_edit"].initial = data.get("gender")
            self.fields["date_of_birth_edit"].initial = data.get("date_of_birth")
            self.fields["location_edit"].initial = data.get("location")
    
    def save(self, commit=True):
        user = super().save(commit)
        submission  = UserSubmission.objects.filter(
            user_id=user.id,
            page__slug="registration-survey"
        ).order_by("-submit_time").first()
        if submission:
            data = submission.form_data.copy()
            data["gender"] = self.cleaned_data["gender_edit"]
            data["date_of_birth"] = self.cleaned_data["date_of_birth_edit"]
            data["location"] = self.cleaned_data["location_edit"]
            submission.form_data = data
            submission.save()

        return user

    class Meta(WagtailUserEditForm.Meta):
        model = User
        fields = WagtailUserEditForm.Meta.fields | {'first_name', 'last_name', 'username', 'display_name', 'terms_accepted', 'groups'}