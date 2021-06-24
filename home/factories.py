import factory
from factory.django import DjangoModelFactory

from home.models import Article, Section


class SectionFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'section{n}')

    class Meta:
        model = Section


class ArticleFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'article{n}')

    class Meta:
        model = Article
