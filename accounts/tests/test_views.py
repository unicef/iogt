from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from wagtail.core.models import Site
from wagtail.tests.utils import WagtailPageTests

from .factories import UserFactory, UserRegistrationPageFactory

User = get_user_model()


class UserLoginView(TestCase):
    def setUp(self):
        self.credentials = {
            "username": "testuser",
            "password": "secret",
        }
        UserFactory.create(
            password=make_password(self.credentials["password"]),
            username=self.credentials["username"],
        )

    def test_login(self):
        response = self.client.post(reverse("accounts:login"), self.credentials, follow=True)
        self.assertTrue(response.context["user"].is_active)

    def test_unsuccessful_login(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "test10",
                "password10": "test10",
            },
            follow=True
        )
        self.assertFalse(response.context["user"].is_active)


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create(password=make_password("test"))

    def test_view_with_auth_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_view_without_auth_user(self):
        """
        """
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(reverse("accounts:login") in response.url)


class UserUpdateViewTest(TestCase):

    def setUp(self):
        username = "test100"
        self.user = UserFactory.create(username=username, password=make_password("test"))
        self.client.force_login(self.user)

    def test_login(self):
        data = {
            "username": "new_username",
            "password": "secret12345689",
            "confirm_password": "secret12345689",
        }
        response = self.client.post(reverse("accounts:update"), data, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data["username"])

