import factory
from factory.django import DjangoModelFactory

from home.models import Article, Section, SiteSettings
from questionnaires.models import Survey


class SectionFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'section{n}')

    class Meta:
        model = Section


class ArticleFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'article{n}')

    class Meta:
        model = Article


class SurveyFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'survey{n}')

    class Meta:
        model = Survey


class SiteSettingsFactory(DjangoModelFactory):
    class Meta:
        model = SiteSettings
