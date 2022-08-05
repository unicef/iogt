import factory
from django.core.files.base import ContentFile
from factory.django import DjangoModelFactory, ImageField
from wagtail.core.models import Locale
from wagtail_factories import PageFactory, ImageFactory, StreamFieldFactory, ImageChooserBlockFactory

from comments.models import CommentStatus
from home.models import (
    Article,
    Section,
    SiteSettings,
    HomePage,
    SVGToPNGMap,
    OfflineContentIndexPage,
    MiscellaneousIndexPage,
)
from questionnaires.models import Survey


class HomePageFactory(PageFactory):
    title = factory.Sequence(lambda n: f'homepage{n}')

    class Meta:
        model = HomePage


class SectionFactory(PageFactory):
    title = factory.Sequence(lambda n: f'section{n}')
    lead_image = factory.SubFactory(ImageFactory)

    class Meta:
        model = Section


class ArticleFactory(PageFactory):
    title = factory.Sequence(lambda n: f'article{n}')
    lead_image = factory.SubFactory(ImageFactory)
    commenting_status = CommentStatus.OPEN
    body = StreamFieldFactory(
        {
            "image": ImageChooserBlockFactory,
        }
    )

    class Meta:
        model = Article


class SVGToPNGMapFactory(DjangoModelFactory):
    png_image_file = factory.LazyAttribute(
            lambda _: ContentFile(
                ImageField()._make_data(
                    {'width': 1024, 'height': 768}
                ), 'example.jpg'
            )
        )

    class Meta:
        model = SVGToPNGMap

class SiteSettingsFactory(DjangoModelFactory):
    class Meta:
        model = SiteSettings

class LocaleFactory(DjangoModelFactory):
    class Meta:
        model = Locale
        django_get_or_create = ('language_code',)


