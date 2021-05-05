import json

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.utils.html import mark_safe

from wagtail.contrib.forms.forms import FormBuilder

# This helps to identify what extra fields needs to be adding to additional info for the users
DEFAULT_USER_FIELDS = ["username", "password", "confirm_password"]


class UserRegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput, strip=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, strip=False)

    class Meta:
        model = get_user_model()
        fields = DEFAULT_USER_FIELDS


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.page = kwargs.pop('page', None)

        super().__init__(*args, **kwargs)
        self.fields["password"].help_text = mark_safe(password_validators_help_text_html())

    def save(self, commit=True):
        password = self.cleaned_data["confirm_password"]
        user = super().save(commit=False)
        user.set_password(password)

        for key in DEFAULT_USER_FIELDS:
            self.cleaned_data.pop(key, None)


        # Add additional info
        user.additional_data = json.dumps(self.cleaned_data)

        user.save()

        return user

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError(
                    "The two password fields didn't match.", code="password_mismatch"
                )
        password_validation.validate_password(confirm_password)
        return confirm_password


class RegistrationFormBuilder(FormBuilder):
    def get_form_class(self):
        return type(str('WagtailForm'), (UserRegistrationForm,), self.formfields)


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, strip=False, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, strip=False, required=False)

    error_messages = {
        'duplicate_username': "A user with that username already exists.",
        'password_mismatch': "The two password fields didn't match.",
    }


    class Meta:
        fields = ('username', 'password1', 'password2')
        model = get_user_model()

    def _clean_username(self):
        username_field = get_user_model().USERNAME_FIELD
        # This method is called even if username if empty, contrary to clean_*
        # methods, so we have to check again here that data is defined.
        if username_field not in self.cleaned_data:
            return
        username = self.cleaned_data[username_field]

        users = get_user_model()._default_manager.all()
        if self.instance.pk is not None:
            users = users.exclude(pk=self.instance.pk)
        if users.filter(**{username_field: username}).exists():
            self.add_error(get_user_model().USERNAME_FIELD, forms.ValidationError(
                self.error_messages['duplicate_username'],
                code='duplicate_username',
            ))
        return username


    def _clean_fields(self):
        super()._clean_fields()
        self._clean_username()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"], code="password_mismatch"
            )
        return password1

    def validate_password(self):
        """
        Run the Django password validators against the new password. This must
        be called after the user instance in self.instance is populated with
        the new data from the form, as some validators rely on attributes on
        the user model.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 == password2:
            password_validation.validate_password(password1, user=self.instance)


    def _post_clean(self):
        super()._post_clean()
        try:
            self.validate_password()
        except forms.ValidationError as e:
            self.add_error('confirm_password', e)

    def save(self, commit=True):
        user = super().save(commit=False)

        # Only set the password if thy entered
        password = self.cleaned_data["password1"]
        if password:
            user.set_password(password)

        user.save()

        return user
