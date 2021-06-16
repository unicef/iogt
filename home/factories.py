import factory
from factory.django import DjangoModelFactory

from home.models import (Article, BannerIndexPage, BannerPage, FeaturedContent,
                         HomePageBanner, Section)


class SectionFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'section{n}')

    class Meta:
        model = Section


class ArticleFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'article{n}')
    live = True

    class Meta:
        model = Article


class FeaturedContentFactory(DjangoModelFactory):
    class Meta:
        model = FeaturedContent


class BannerIndexPageFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'banner index{n}')

    class Meta:
        model = BannerIndexPage


class BannerPageFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: f'banner{n}')

    class Meta:
        model = BannerPage


class HomePageBannerFactory(DjangoModelFactory):
    class Meta:
        model = HomePageBanner
