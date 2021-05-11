from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from wagtail.core.models import Site
from wagtail.tests.utils import WagtailPageTests

from .factories import UserFactory, UserRegistrationPageFactory

User = get_user_model()

class UserTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_create(self):
        self.assertIsNotNone(self.user.id)


class UserRegistrationPageTest(WagtailPageTests):

    def setUp(self):
        site = Site.objects.get()
        self.root = site.root_page.specific
        self.registration_page = UserRegistrationPageFactory.create(parent=self.root)

    def test_create(self):
        self.assertIsNotNone(self.registration_page.id)

    def test_render(self):
        response = self.client.get(self.registration_page.get_url())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue("form" in response.context)


    def test_create_user(self):
        username = "Test100"
        response = self.client.post(
            self.registration_page.get_url(),
            {
                'username': username,
                'password': "testing100",
                'confirm_password': "testing100",
            }
        )
        self.assertTrue(User.objects.filter(username=username).exists())
