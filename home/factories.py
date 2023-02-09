import factory
from django.core.files.base import ContentFile
from factory.django import DjangoModelFactory, ImageField
from wagtail.core.models import Locale
from wagtail_factories import (
    ImageChooserBlockFactory,
    ImageFactory,
    PageFactory,
    StreamFieldFactory,
)
from wagtail_factories.blocks import ChooserBlockFactory, BlockFactory
from wagtail_factories.factories import CollectionMemberFactory
from wagtailmedia.models import get_media_model

from comments.models import CommentStatus
from home.blocks import MediaBlock
from home.models import (
    Article,
    FooterIndexPage,
    BannerIndexPage,
    BannerPage,
    HomePage,
    MiscellaneousIndexPage,
    OfflineContentIndexPage,
    SVGToPNGMap,
    Section,
    SectionIndexPage,
    SiteSettings,
)


class HomePageFactory(PageFactory):
    title = factory.Sequence(lambda n: f'homepage{n}')

    class Meta:
        model = HomePage

class SectionIndexFactory(PageFactory):
    title = 'Sections'

    class Meta:
        model = SectionIndexPage

class SectionFactory(PageFactory):
    title = factory.Sequence(lambda n: f'section{n}')
    lead_image = factory.SubFactory(ImageFactory)
    image_icon = factory.SubFactory(ImageFactory)

    class Meta:
        model = Section


class MediaFactory(CollectionMemberFactory):
    class Meta:
        model = get_media_model()

    title = factory.Sequence(lambda n: f'media{n}')
    file = factory.django.FileField()


class MediaBlockFactory(BlockFactory):
    media = factory.SubFactory(MediaFactory)

    class Meta:
        model = MediaBlock


class ArticleFactory(PageFactory):
    title = factory.Sequence(lambda n: f'article{n}')
    lead_image = factory.SubFactory(ImageFactory)
    commenting_status = CommentStatus.OPEN
    body = StreamFieldFactory(
        {
            "image": factory.SubFactory(ImageChooserBlockFactory),
            "media": factory.SubFactory(MediaBlockFactory),
        }
    )

    class Meta:
        model = Article


class MiscellaneousIndexPageFactory(PageFactory):
    title = factory.Sequence(lambda n: f'miscellaneous{n}')

    class Meta:
        model = MiscellaneousIndexPage


class OfflineContentIndexPageFactory(ArticleFactory):
    title = factory.Sequence(lambda n: f'offline-content-index{n}')

    class Meta:
        model = OfflineContentIndexPage


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

class FooterIndexPageFactory(PageFactory):
    title = 'Footers'

    class Meta:
        model = FooterIndexPage

class BannerIndexPageFactory(PageFactory):
    title = 'Banners'

    class Meta:
        model = BannerIndexPage

class BannerFactory(PageFactory):

    title = factory.Sequence(lambda n: f'banner{n}')
    banner_image = factory.SubFactory(ImageFactory)
    class Meta:
        model = BannerPage

