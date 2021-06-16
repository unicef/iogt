from django.test import TestCase
from django.urls import reverse

from iogt_users.factories import UserFactory
from iogt_users.forms import AccountSignupForm


class UserSignupFormTests(TestCase):
    def test_valid_signup(self):
        form_data = {
            'display_name': 'John Doe',
            'terms_accepted': True,
            'username': 'john_doe',
            'password1': '1234',
            'password2': '1234',
            'email': 'john@example.com'
        }
        form = AccountSignupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_signup_without_required_fields(self):
        form_data = {
            'terms_accepted': True,
            'username': 'john_doe',
            'password1': '1234',
            'password2': '1234',
        }
        form = AccountSignupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_long_password_is_invalid(self):
        form_data = {
            'display_name': 'John Doe',
            'terms_accepted': True,
            'username': 'john_doe',
            'password1': 'test@123',
            'password2': 'test@123',
            'email': 'john@example.com'
        }
        form = AccountSignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password1'], ['Ensure this value has at most 4 characters (it has 8).'])
        self.assertEqual(form.errors['password2'], ['Ensure this value has at most 4 characters (it has 8).'])


class UserProfileDetailViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory(has_filled_registration_survey=True)
        self.client.force_login(self.user)
        self.url = reverse('user_profile')

    def test_user_profile_detail(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        self.assertTemplateUsed(response, 'profile.html')


class UserProfileEditViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory(has_filled_registration_survey=True)
        self.client.force_login(self.user)
        self.url = reverse('user_profile_edit')

    def test_user_profile_edit(self):
        data = {
            'display_name': 'Doe John',
            'email': 'doejohn@example.com',
        }

        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_profile_edit'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.display_name, 'Doe John')
        self.assertEqual(self.user.email, 'doejohn@example.com')
