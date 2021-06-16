from django.contrib.auth import get_user_model
import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    display_name = 'John Doe'
    username = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.LazyFunction(lambda: make_password('test@123'))

    class Meta:
        model = get_user_model()


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
