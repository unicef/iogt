import factory
from factory.django import DjangoModelFactory

from home.models import Article


class ArticleFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'article{n}')

    class Meta:
        model = Article
