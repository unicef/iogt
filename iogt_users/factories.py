from django.contrib.auth import get_user_model
import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from factory.django import DjangoModelFactory
from wagtail.models import GroupPagePermission


class UserFactory(DjangoModelFactory):
    first_name = 'John'
    last_name = 'Doe'
    username = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.LazyFunction(lambda: make_password('test@123'))
    has_filled_registration_survey = True

    class Meta:
        model = get_user_model()


class AdminUserFactory(UserFactory):
    is_superuser = True

class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group


class GroupPagePermissionFactory(DjangoModelFactory):
    permission_type = 'edit'

    class Meta:
        model = GroupPagePermission
