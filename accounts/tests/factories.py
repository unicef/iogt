from django.contrib.auth import get_user_model

from accounts.models import UserRegistrationPage

import factory
import wagtail_factories

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "username{0}".format(n))
    email = factory.Sequence(lambda n: "person{0}@email.com".format(n))

    class Meta:
        model = User


class UserRegistrationPageFactory(wagtail_factories.PageFactory):
    title = factory.Sequence(lambda n: f"Story Index Page {n}")
    slug = factory.Sequence(lambda n: f"story-index-page-{n}")

    class Meta:
        model = UserRegistrationPage

