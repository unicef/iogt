import factory

from home.models import Article
from home.tests.faker import faker


class ArticleFactory(factory.django.DjangoModelFactory):
    title = factory.LazyAttribute(lambda x: faker.pystr())
    path = factory.LazyAttribute(lambda x: "000100010001")
    depth = 3

    class Meta:
        model = Article
