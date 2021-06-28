from allauth.account.forms import SignupForm, PasswordField
from allauth.utils import set_form_field_order
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import DateField, Field, ChoiceField
from wagtail.users.forms import UserEditForm as WagtailUserEditForm, \
    UserCreationForm as WagtailUserCreationForm, \
    custom_fields

from .models import User
from .utils import get_wagtail_admin_user_standard_fields


class SelectWidget(forms.Select):
    """
    Subclass of Django's select widget that allows disabling options.
    """

    def __init__(self, *args, **kwargs):
        self._disabled_choices = []
        super().__init__(*args, **kwargs)

    @property
    def disabled_choices(self):
        return self._disabled_choices

    @disabled_choices.setter
    def disabled_choices(self, other):
        self._disabled_choices = other

    def create_option(self, name, value, *args, **kwargs):
        option_dict = super().create_option(name, value, *args, **kwargs)
        if value in self.disabled_choices:
            option_dict['attrs']['disabled'] = 'disabled'
        return option_dict


class AccountSignupForm(SignupForm):
    choises = [(None, 'Tell us your gender'), ('M', 'Male'),
               ('F', 'Female')]
    field_order = [
        "username",
        "password1",
        "date",
        "gender"
    ]

    def __init__(self, *args, **kwargs):
        super(AccountSignupForm, self).__init__(*args, **kwargs)
        self.fields["username"] = Field(
            label="Create Username",
            help_text="Invalid Username",
            widget=forms.TextInput(
                attrs={'type': 'text', 'placeholder': 'Create Username'})
        )
        self.fields["password1"] = PasswordField(
            autocomplete="new-password",
            label="Create 4 digit pin",
            help_text="Invalid Pin",
            max_length=4,
            widget=forms.TextInput(
                attrs={'type': 'password'})
        )
        self.fields["date"] = DateField(
            help_text="Invalid Date",
            input_formats=["%d/%m/%Y"],
            widget=forms.DateInput(
                format="%d/%m/%Y",
                attrs={"type": "date"}
            )
        )
        self.fields["gender"] = ChoiceField(
            required=True,
            help_text="Choose your gender",
            choices=self.choises,
            widget=forms.Select(
                attrs={"class": "cust-select profile-form__input"}),
        )

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    def save(self, request):
        user = super(AccountSignupForm, self).save(request)
        return user


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
    display_name = forms.CharField(label='Display Name', required=False,
                                   max_length=150)
    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')

    class Meta(WagtailUserCreationForm.Meta):
        fields = set([
            User.USERNAME_FIELD]) | get_wagtail_admin_user_standard_fields() | custom_fields


class WagtailAdminUserEditForm(WagtailUserEditForm):
    email = forms.EmailField(required=False, label='Email')
    first_name = None
    last_name = None
    display_name = forms.CharField(label='Display Name', required=False,
                                   max_length=150)
    terms_accepted = forms.BooleanField(label='I accept the terms & conditions')

    class Meta(WagtailUserEditForm.Meta):
        fields = set([User.USERNAME_FIELD,
                      "is_active"]) | get_wagtail_admin_user_standard_fields() | custom_fields
