import logging
import os

from django.conf import settings
from django.contrib.admin.utils import flatten
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.images import get_image_dimensions
from django.core.cache import cache
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from iogt.settings.base import WAGTAIL_CONTENT_LANGUAGES
from modelcluster.fields import ParentalKey
from rest_framework import status
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface
)
from wagtail.contrib.settings.models import BaseSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Orderable, Page, Site, Locale
from wagtail.core.rich_text import get_text_for_indexing
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.search import index
from wagtailmarkdown.blocks import MarkdownBlock
from wagtailmenus.models import AbstractFlatMenuItem, BooleanField
from wagtailsvg.models import Svg
from wagtailsvg.edit_handlers import SvgChooserPanel

from messaging.blocks import ChatBotButtonBlock
from comments.models import CommentableMixin, CannedResponse
from .blocks import (
    MediaBlock, SocialMediaLinkBlock, SocialMediaShareButtonBlock, EmbeddedPollBlock, EmbeddedSurveyBlock,
    EmbeddedQuizBlock, PageButtonBlock, NumberedListBlock, RawHTMLBlock, ArticleBlock, DownloadButtonBlock,
)
from .forms import SectionPageForm
from .mixins import PageUtilsMixin, TitleIconMixin
from .utils.image import convert_svg_to_png_bytes
from .utils.progress_manager import ProgressManager
import iogt.iogt_globals as globals_

User = get_user_model()
logger = logging.getLogger(__name__)


class HomePage(Page, PageUtilsMixin, TitleIconMixin):
    parent_page_types = ['wagtailcore.page']
    template = 'home/home_page.html'
    show_in_menus_default = True

    home_featured_content = StreamField([
        ('page_button', PageButtonBlock()),
        ('embedded_poll', EmbeddedPollBlock()),
        ('embedded_survey', EmbeddedSurveyBlock()),
        ('embedded_quiz', EmbeddedQuizBlock()),
        ('article', ArticleBlock()),
        ('download', DownloadButtonBlock()),
    ], null=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            InlinePanel('home_page_banners', label=_("Home Page Banner")),
        ], heading=_('Home Page Banners')),
        StreamFieldPanel('home_featured_content')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        banners = []
        for home_page_banner in self.home_page_banners.select_related('banner_page', 'banner_page__banner_link_page').all():
            banner_page = home_page_banner.banner_page
            if banner_page.live and ((banner_page.banner_link_page and banner_page.banner_link_page.live) or
                                     banner_page.banner_link_page == None):
                banners.append(banner_page.specific)
        context['banners'] = banners
        return context

    @property
    def get_image_urls(self):
        return self._get_stream_data_image_urls(self.home_featured_content.raw_data)


class FeaturedContent(Orderable):
    source = ParentalKey(Page, related_name='featured_content',
                         on_delete=models.CASCADE, blank=True)
    content = models.ForeignKey(Page, on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('content'),
    ]


class HomePageBanner(Orderable):
    source = ParentalKey(Page, related_name='home_page_banners',
                         on_delete=models.CASCADE, blank=True)
    banner_page = models.ForeignKey('home.BannerPage', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('banner_page'),
    ]


class SectionTaggedItem(TaggedItemBase):
    """The through model between Section and Tag"""
    content_object = ParentalKey('Section', related_name='tagged_items',
                                 on_delete=models.CASCADE)


class ArticleTaggedItem(TaggedItemBase):
    """The through model between Article and Tag"""
    content_object = ParentalKey('Article', related_name='tagged_items',
                                 on_delete=models.CASCADE)


class SectionIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.Section']

    @classmethod
    def get_top_level_sections(cls):
        section_index_page = cls.objects.filter(locale=Locale.get_active()).first()
        if section_index_page:
            return section_index_page.get_children().live().specific()
        return cls.objects.none()


class Section(Page, PageUtilsMixin, CommentableMixin, TitleIconMixin):
    lead_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    icon = models.ForeignKey(
        Svg,
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    image_icon = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    background_color = models.CharField(
        max_length=8,
        blank=True,
        null=True,
    )
    font_color = models.CharField(
        max_length=8,
        blank=True,
        null=True,
    )
    body = StreamField([
        ('download', DownloadButtonBlock()),
    ], null=True, blank=True)

    tags = ClusterTaggableManager(through='SectionTaggedItem', blank=True)
    show_progress_bar = models.BooleanField(default=False)
    larger_image_for_top_page_in_list_as_in_v1 = models.BooleanField(default=False)

    show_in_menus_default = True

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([FieldPanel("tags"), ], heading='Metadata'),
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('lead_image'),
        SvgChooserPanel('icon'),
        ImageChooserPanel('image_icon'),
        FieldPanel('background_color'),
        FieldPanel('font_color'),
        FieldPanel('larger_image_for_top_page_in_list_as_in_v1'),
        MultiFieldPanel([
            InlinePanel('featured_content', max_num=1,
                        label=_("Featured Content")),
        ], heading=_('Featured Content')),
        StreamFieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('show_progress_bar')
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(settings_panels, heading='Settings'),
        ObjectList(CommentableMixin.comments_panels, heading='Comments')
    ])

    base_form_class = SectionPageForm

    def get_descendant_articles(self):
        return Article.objects.descendant_of(self).live().exact_type(Article)

    def get_progress_bar_enabled_ancestor(self):
        return Section.objects.ancestor_of(self, inclusive=True).exact_type(
            Section).live().filter(
            show_progress_bar=True).first()

    def get_user_progress_dict(self, request):
        progress_manager = ProgressManager(request)
        read_article_count, total_article_count = progress_manager.get_progress(self)
        return {
            'read': read_article_count,
            'total': total_article_count,
            'range_': list(range(total_article_count)) if total_article_count else 0,
            'width_': 100 / total_article_count if total_article_count else 0,
        }

    def is_complete(self, request):
        progress_manager = ProgressManager(request)
        return progress_manager.is_section_complete(self)

    def get_context(self, request):
        context = super().get_context(request)
        featured_content = self.featured_content.all().first()
        context['featured_content'] = featured_content.content.specific if featured_content and featured_content.content.live else None
        context['children'] = self.get_children().live().specific()
        context['user_progress'] = self.get_user_progress_dict(request)

        return context

    @staticmethod
    def get_progress_bar_eligible_sections():
        """
        Eligibility criteria:
        Sections whose ancestors don't have show_progress_bar=True are eligible to
        show progress bars.
        :return:e
        """
        progress_bar_sections = Section.objects.filter(show_progress_bar=True)
        all_descendants = [list(
            Section.objects.type(Section).descendant_of(section).values_list(
                'pk', flat=True)) for
            section in
            progress_bar_sections]
        all_descendants = set(flatten(all_descendants))

        return Section.objects.exclude(pk__in=all_descendants)

    @property
    def get_image_urls(self):
        image_urls = []

        if self.lead_image:
            image_urls += self._get_renditions(self.lead_image)

        if self.image_icon:
            image_urls += self._get_renditions(self.image_icon)

        image_urls += self._get_stream_data_image_urls(self.body.raw_data)

        return image_urls

    class Meta:
        verbose_name = _("section")
        verbose_name_plural = _("sections")


class ArticleRecommendation(Orderable):
    source = ParentalKey('Article', related_name='recommended_articles',
                         on_delete=models.CASCADE, blank=True)
    article = models.ForeignKey('Article', on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('article')
    ]


class AbstractArticle(Page, PageUtilsMixin, CommentableMixin, TitleIconMixin):
    lead_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    icon = models.ForeignKey(
        Svg,
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    image_icon = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    index_page_description = models.TextField(null=True, blank=True)

    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title", template='blocks/heading.html')),
        ('paragraph', blocks.RichTextBlock(features=settings.WAGTAIL_RICH_TEXT_FIELD_FEATURES)),
        ('markdown', MarkdownBlock(icon='code')),
        ('paragraph_v1_legacy', RawHTMLBlock(icon='code')),
        ('image', ImageChooserBlock(template='blocks/image.html')),
        ('list', blocks.ListBlock(MarkdownBlock(icon='code'))),
        ('numbered_list', NumberedListBlock(MarkdownBlock(icon='code'))),
        ('page_button', PageButtonBlock()),
        ('embedded_poll', EmbeddedPollBlock()),
        ('embedded_survey', EmbeddedSurveyBlock()),
        ('embedded_quiz', EmbeddedQuizBlock()),
        ('media', MediaBlock(icon='media')),
        ('chat_bot', ChatBotButtonBlock()),
        ('download', DownloadButtonBlock()),
    ])
    show_in_menus_default = True

    content_panels = Page.content_panels + [
        ImageChooserPanel('lead_image'),
        SvgChooserPanel('icon'),
        ImageChooserPanel('image_icon'),
        StreamFieldPanel('body'),
        FieldPanel('index_page_description'),
    ]

    edit_handler_list = [
        ObjectList(content_panels, heading='Content'),
        ObjectList(Page.settings_panels, heading='Settings'),
        ObjectList(CommentableMixin.comments_panels, heading='Comments')
    ]

    edit_handler = TabbedInterface(edit_handler_list)

    search_fields = Page.search_fields + [
        index.SearchField('get_heading_values', partial_match=True, boost=1),
        index.SearchField('get_paragraph_values', partial_match=True),
    ]

    def _get_child_block_values(self, block_type):
        searchable_content = []
        for block in self.body:
            if block.block_type == block_type:
                value = force_str(block.value)
                searchable_content.append(get_text_for_indexing(value))
        return searchable_content

    def get_heading_values(self):
        heading_values = self._get_child_block_values('heading')
        return '\n'.join(heading_values)

    def get_paragraph_values(self):
        paragraph_values = self._get_child_block_values('paragraph')
        return '\n'.join(paragraph_values)

    def get_progress_enabled_section(self):
        """
        Returning .first() will bypass any discrepancies in settings show_progress_bar=True
        for sections
        :return:
        """
        return Section.objects.ancestor_of(self).type(Section).filter(
            show_progress_bar=True).first()

    def get_context(self, request):
        context = super().get_context(request)

        progress_enabled_section = self.get_progress_enabled_section()
        if progress_enabled_section:
            context.update({
                'user_progress': progress_enabled_section.get_user_progress_dict(
                    request)
            })

        return context

    def description(self):
        for block in self.body:
            if block.block_type == 'paragraph':
                return block
        return ''

    def is_complete(self, request):
        progress_manager = ProgressManager(request)
        return progress_manager.is_article_complete(self)

    @property
    def top_level_section(self):
        return self.get_ancestors().filter(depth=4).first().specific

    @property
    def get_image_urls(self):
        image_urls = []

        if self.lead_image:
            image_urls += self._get_renditions(self.lead_image)

        if self.image_icon:
            image_urls += self._get_renditions(self.image_icon)

        image_urls += self._get_stream_data_image_urls(self.body.raw_data)

        return image_urls

    class Meta:
        abstract = True
        verbose_name = _("article")
        verbose_name_plural = _("articles")


class Article(AbstractArticle):
    tags = ClusterTaggableManager(through='ArticleTaggedItem', blank=True)

    content_panels = AbstractArticle.content_panels + [
        MultiFieldPanel([
            InlinePanel('recommended_articles',
                        label=_("Recommended Articles")),
        ],
            heading='Recommended Content')
    ]

    promote_panels = AbstractArticle.promote_panels + [
        MultiFieldPanel([FieldPanel("tags"), ], heading='Metadata'),
    ]

    edit_handler_list = AbstractArticle.edit_handler_list + [
        ObjectList(promote_panels, heading='Promote'),
    ]

    edit_handler = TabbedInterface(edit_handler_list)

    def get_context(self, request):
        context = super().get_context(request)
        context['recommended_articles'] = [
            recommended_article.article.specific
            for recommended_article in self.recommended_articles.all() if recommended_article.article.live
        ]

        return context

    def serve(self, request):
        response = super().serve(request)
        if response.status_code == status.HTTP_200_OK:
            User.record_article_read(request=request, article=self)
        return response


class MiscellaneousIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.OfflineContentIndexPage']


class OfflineContentIndexPage(AbstractArticle):
    template = 'home/article.html'
    parent_page_types = ['home.MiscellaneousIndexPage']
    subpage_types = []

    class Meta:
        verbose_name = 'Offline Content Index Page'


class BannerIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.BannerPage']


class BannerPage(Page, PageUtilsMixin):
    parent_page_types = ['home.BannerIndexPage']
    subpage_types = []

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        on_delete=models.PROTECT,
        null=True, blank=True,
        help_text=_('Image to display as the banner')
    )
    banner_link_page = models.ForeignKey(
        Page, null=True, blank=True, related_name='banners',
        on_delete=models.SET_NULL,
        help_text=_('Optional page to which the banner will link to'))

    content_panels = Page.content_panels + [
        ImageChooserPanel('banner_image'),
        PageChooserPanel('banner_link_page'),
    ]

    @property
    def get_image_urls(self):
        image_urls = []

        if self.banner_image:
            image_urls += self._get_renditions(self.banner_image)

        return image_urls


class FooterIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = [
        'home.Section', 'home.Article', 'home.PageLinkPage', 'questionnaires.Poll',
        'questionnaires.Survey', 'questionnaires.Quiz',
    ]

    @classmethod
    def get_active_footers(cls):
        footer_index_page = cls.objects.filter(locale=Locale.get_active()).first()
        if footer_index_page:
            footers = footer_index_page.get_children().live().specific()
            return [footer for footer in footers if footer.get_page()]
        return cls.objects.none()

    def __str__(self):
        return self.title


class FooterPage(Article, TitleIconMixin):
    parent_page_types = []
    subpage_types = []
    template = 'home/article.html'

    class Meta:
        verbose_name = _("footer")
        verbose_name_plural = _("footers")


class PageLinkPage(Page, PageUtilsMixin, TitleIconMixin):
    parent_page_types = ['home.FooterIndexPage', 'home.Section']
    subpage_types = []
    show_in_menus_default = True

    icon = models.ForeignKey(
        Svg,
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    image_icon = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )

    page = models.ForeignKey(Page, null=True, blank=True, related_name='page_link_pages', on_delete=models.PROTECT)
    external_link = models.URLField(null=True, blank=True)

    content_panels = Page.content_panels + [
        SvgChooserPanel('icon'),
        ImageChooserPanel('image_icon'),
        PageChooserPanel('page'),
        FieldPanel('external_link'),
    ]

    def get_page(self):
        return self.page.specific if self.page and self.page.live else self

    def get_icon(self):
        icon = super().get_icon()
        if not icon.url and self.page and self.page.live:
            icon = self.page.specific.get_icon()

        return icon

    def get_url(self, request=None, current_site=None):
        url = ''
        if self.page and self.page.live:
            url = self.page.specific.url
        elif self.external_link:
            url = self.external_link

        return url

    url = property(get_url)


@register_setting
class SiteSettings(BaseSetting):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Upload an image file (.jpg, .png). The ideal size is 120px x 48px"
    )
    favicon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Upload an image file (.jpg, .png). The ideal size is 40px x 40px"
    )
    apple_touch_icon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Upload an image file (.jpg, .png) to be used as apple touch icon. "
                  "The ideal size is 120px x 120px"
    )
    show_only_translated_pages = models.BooleanField(
        default=False,
        help_text=_('When selecting this option, untranslated pages'
                    ' will not be visible to the front end user'
                    ' when viewing a child language of the site'))
    # TODO: GA, FB analytics should be global.
    fb_analytics_app_id = models.CharField(
        verbose_name=_('Facebook Analytics App ID'),
        max_length=25,
        null=True,
        blank=True,
        help_text=_(
            "The tracking ID to be used to view Facebook Analytics")
    )
    local_ga_tag_manager = models.CharField(
        verbose_name=_('Local GA Tag Manager'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Local GA Tag Manager tracking code (e.g GTM-XXX) to be used to "
            "view analytics on this site only")
    )
    global_ga_tag_manager = models.CharField(
        verbose_name=_('Global GA Tag Manager'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Global GA Tag Manager tracking code (e.g GTM-XXX) to be used"
            " to view analytics on more than one site globally")
    )
    local_ga_tracking_code = models.CharField(
        verbose_name=_('Local GA Tracking Code'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Local GA tracking code to be used to "
            "view analytics on this site only")
    )
    global_ga_tracking_code = models.CharField(
        verbose_name=_('Global GA Tracking Code'),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Global GA tracking code to be used"
            " to view analytics on more than one site globally")
    )
    social_media_link = StreamField([
        ('social_media_link', SocialMediaLinkBlock()),
    ], null=True, blank=True)
    social_media_content_sharing_button = StreamField([
        ('social_media_content_sharing_button', SocialMediaShareButtonBlock()),
    ], null=True, blank=True)
    media_file_size_threshold = models.IntegerField(
        default=9437184,
        help_text=_('Show warning if uploaded media file size is greater than this in bytes. Default is 9 MB'))
    allow_anonymous_comment = models.BooleanField(default=False)
    registration_survey = models.ForeignKey('questionnaires.Survey', null=True,
                                            blank=True,
                                            on_delete=models.SET_NULL)
    opt_in_to_google_web_light = models.BooleanField(default=False)

    panels = [
        ImageChooserPanel('logo'),
        ImageChooserPanel('favicon'),
        ImageChooserPanel('apple_touch_icon'),
        MultiFieldPanel(
            [
                FieldPanel('show_only_translated_pages'),
            ],
            heading="Multi Language",
        ),
        MultiFieldPanel(
            [
                FieldPanel('fb_analytics_app_id'),
            ],
            heading="Facebook Analytics Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('local_ga_tag_manager'),
                FieldPanel('global_ga_tag_manager'),
            ],
            heading="GA Tag Manager Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('local_ga_tracking_code'),
                FieldPanel('global_ga_tracking_code'),
            ],
            heading="GA Tracking Code Settings",
        ),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        StreamFieldPanel('social_media_link'),
                    ],
                    heading="Social Media Footer Page", ),
            ],
            heading="Social Media Page Links", ),
        MultiFieldPanel(
            [
                MultiFieldPanel(
                    [
                        StreamFieldPanel('social_media_content_sharing_button'),
                    ],
                    heading="Social Media Content Sharing Buttons", ),
            ],
            heading="Social Media Content Sharing Buttons", ),
        MultiFieldPanel(
            [
                FieldPanel('media_file_size_threshold'),
            ],
            heading="Media File Size Threshold",
        ),
        MultiFieldPanel(
            [
                FieldPanel('allow_anonymous_comment'),
            ],
            heading="Allow Anonymous Comment",
        ),
        MultiFieldPanel(
            [
                PageChooserPanel('registration_survey'),
            ],
            heading="Registration Settings",
        ),
        MultiFieldPanel(
            [
                FieldPanel('opt_in_to_google_web_light'),
            ],
            heading="Opt in to Google web light",
        ),
    ]

    @classmethod
    def get_for_default_site(cls):
        default_site = Site.objects.filter(is_default_site=True).first()
        return cls.for_site(default_site)

    def __str__(self):
        return self.site.site_name

    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')


class IogtFlatMenuItem(AbstractFlatMenuItem, TitleIconMixin):
    menu = ParentalKey(
        'wagtailmenus.FlatMenu',
        on_delete=models.CASCADE,
        related_name="iogt_flat_menu_items",
    )
    link_url = models.CharField(
        verbose_name=_('link to a custom URL'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_(
            'If you are linking back to a URL on your own IoGT site, be sure to remove the domain and everything '
            'before it. For example "http://sd.goodinternet.org/url/" should instead be "/url/".'
        ),
    )
    icon = models.ForeignKey(
        Svg,
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('If Page link is a section page and icon is blank then the section icon will be used. '
                    'Specify an icon here to override this.')
    )
    image_icon = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )

    background_color = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_('The background color of the flat menu item on Desktop + Mobile')
    )

    font_color = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_('The font color of the flat menu item on Desktop + Mobile')
    )
    display_only_in_single_column_view = models.BooleanField(default=False)

    panels = [
        PageChooserPanel('link_page'),
        FieldPanel('link_url', classname='red-help-text'),
        FieldPanel('url_append'),
        FieldPanel('link_text'),
        FieldPanel('handle'),
        FieldPanel('allow_subnav'),
        SvgChooserPanel('icon'),
        ImageChooserPanel('image_icon'),
        FieldPanel('background_color'),
        FieldPanel('font_color'),
        FieldPanel('display_only_in_single_column_view'),
    ]

    def get_icon(self):
        icon = super().get_icon()
        if not icon.url and self.link_page and hasattr(self.link_page, 'get_icon'):
            icon = self.link_page.get_icon()

        return icon

    def get_background_color(self):
        theme_settings = globals_.theme_settings
        return self.background_color or theme_settings.navbar_background_color

    def get_font_color(self):
        theme_settings = globals_.theme_settings
        return self.font_color or theme_settings.navbar_font_color

    def get_single_column_view(self):
        return 'single-column-view' if self.display_only_in_single_column_view else ''


@deconstructible
class ImageValidator:
    def __init__(self, width=None, height=None):
        self.width = width
        self.height = height

    def __call__(self, image):
        img = Image.objects.get(id=image)

        w, h = get_image_dimensions(img.file)
        ext = os.path.splitext(img.filename)[1]
        valid_extensions = [".png"]

        if not ext.lower() in valid_extensions:
            raise ValidationError("Only .png images can be used")

        if self.width is not None and w != self.width:
            raise ValidationError(
                f"({img.filename} - Width: {w}px, Height: {h}px) - The width image must be {self.width}px"
            )

        if self.height is not None and h != self.height:
            raise ValidationError(
                f"({img.filename} - Height: {h}px, Width: {w}px) - The height image must be {self.height}px "
            )


class ManifestSettings(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Provide name that usually represents the name of the web application to user"),
    )
    short_name = models.CharField(
        max_length=255,
        verbose_name=_("Short name"),
        help_text=_("Provide short name to be displayed, if there is not enough space to display full name"),
    )
    scope = models.CharField(
        max_length=255,
        verbose_name=_("Scope"),
        help_text=_(
            "Provide navigation scope to limit what web pages can be viewed "
            "Example: 'https://www.iogt.com/<page-url>/' limits navigation "
            "to <page-url> of https://www.iogt.com:"
        ),
    )
    start_url = models.CharField(
        max_length=255,
        verbose_name=_("Start URL"),
        help_text=_(
            "Start URL is the preferred URL that should be loaded "
            "when the user launches the web application"
        ),
    )
    display = models.CharField(
        max_length=255,
        choices=[
            ('FULLSCREEN', 'fullscreen'),
            ('STANDALONE', 'standalone'),
            ('MINIMAL_UI', 'minimal-ui'),
            ('BROWSER', 'browser')
        ],
        verbose_name=_("Browser UI"),
        help_text=_(
            "Determines the preferred display mode for the website. The possible values are: "
            "'fullscreen', 'standalone', 'minimal-ui', 'browser'. A better choice would be to use standalone "
            "as it looks great on mobile as well. For further information refer to: "
            "https://developer.mozilla.org/en-US/docs/Web/Manifest/display#values"
        ),
    )
    background_color = models.CharField(
        max_length=10,
        verbose_name=_("Background color"),
        help_text=_(
            "Background color member defines a placeholder background color "
            "for the application page to display before its stylesheet is loaded. (example: #FFF)"
        ),
    )
    theme_color = models.CharField(
        max_length=10,
        verbose_name=_("Theme color"),
        help_text=_("Theme color defines the default theme color for the application (example: #493174)"),
    )
    description = models.CharField(
        max_length=500,
        verbose_name=_("Description"),
        help_text=_("Provide description for application"),
    )
    language = models.CharField(
        max_length=3,
        choices=WAGTAIL_CONTENT_LANGUAGES,
        default="en",
        verbose_name=_("Language"),
        help_text=_("Choose language"),
    )
    icon_96_96 = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
        verbose_name=_("Icon 96x96"),
        help_text=_("Add PNG icon 96x96 px"),
        validators=[ImageValidator(width=96, height=96)],
    )
    icon_512_512 = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
        verbose_name=_("Icon 512x512"),
        help_text=_("Add PNG icon 512x512 px"),
        validators=[ImageValidator(width=512, height=512)],
    )
    icon_192_192 = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
        verbose_name=_("Icon 192x192 (maskable)"),
        help_text=_(
            "Add PNG icon 192x192 px (maskable image can be created using https://maskable.app/)"
        ),
        validators=[ImageValidator(width=192, height=192)],
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("language"),
            ],
            heading="Language",
        ),
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("short_name"),
                FieldPanel("description"),
                FieldPanel("scope"),
                FieldPanel("start_url"),
                FieldPanel("display"),
            ],
            heading="Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("theme_color"),
                FieldPanel("background_color"),
            ],
            heading="Colors",
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel("icon_96_96"),
                ImageChooserPanel("icon_512_512"),
                ImageChooserPanel("icon_192_192"),
            ],
            heading="Icons",
        ),
    ]

    def __str__(self):
        return f"Manifest for {self.name} - {self.language}"

    class Meta:
        unique_together = (
            "language",
            "scope",
        )
        verbose_name = "Manifest settings"
        verbose_name_plural = "Manifests settings"


@register_setting
class ThemeSettings(BaseSetting):
    global_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the website',
        max_length=8, default='#FFFFFF')

    header_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the header background as a HEX code', max_length=8,
        default='#FFFFFF')

    language_picker_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the language picker button as a HEX code',
        max_length=8, default='#FDD256')
    language_picker_font_color = models.CharField(
        null=True, blank=True, help_text='The font color of the language picker button as a HEX code',
        max_length=8, default='#303030')

    section_listing_questionnaire_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the Questionnaire in section listing as a HEX code',
        max_length=8, default='#f0f0f0')
    section_listing_questionnaire_font_color = models.CharField(
        null=True, blank=True, help_text='The font color of the Questionnaire in section listing as a HEX code',
        max_length=8, default='#444')

    section_card_font_color = models.CharField(
        null=True, blank=True, help_text='The background color of the sub section as a HEX code',
        max_length=8, default='#444')
    section_card_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the sub section as a HEX code',
        max_length=8, default='#ffffff')

    article_card_font_color = models.CharField(
        null=True, blank=True, help_text='The background color of the Embedded Article in Home > Featured Content'
                                         ' as a HEX code', max_length=8, default='#444')
    article_card_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the Embedded Article in Home > Featured Content'
                                         ' as a HEX code', max_length=8, default='#ffffff')

    primary_button_font_color = models.CharField(
        null=True, blank=True, help_text='The font/icon color of the primary button as a HEX code', max_length=8,
        default='#444')
    primary_button_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the primary button as a HEX code', max_length=8,
        default='#f0f0f0')

    navbar_background_color = models.CharField(
        null=True, blank=True, help_text='The background color of the navbar as a HEX code', max_length=8,
        default='#0094F4')
    navbar_font_color = models.CharField(
        null=True, blank=True, help_text='The font color of the navbar as a HEX code', max_length=8,
        default='#FFFFFF')


class V1ToV2ObjectMap(models.Model):
    v1_object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    extra = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.v1_object_id} -> {self.object_id}'

    @classmethod
    def get_v1_id(cls, klass, object_id, extra=None):
        content_type = ContentType.objects.get_for_model(klass)

        try:
            return cls.objects.get(content_type=content_type, object_id=object_id, extra=extra).v1_object_id
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_v2_obj(cls, klass, v1_object_id, extra=None):
        content_type = ContentType.objects.get_for_model(klass)

        try:
            return cls.objects.get(content_type=content_type, v1_object_id=v1_object_id, extra=extra).content_object
        except ObjectDoesNotExist:
            return None

    @classmethod
    def create_map(cls, content_object, v1_object_id, extra=None):
        content_type = ContentType.objects.get_for_model(type(content_object))
        obj, __ = cls.objects.get_or_create(content_type=content_type, object_id=content_object.pk,
                                            v1_object_id=v1_object_id, extra=extra)
        return obj


class SVGToPNGMap(models.Model):
    svg_path = models.TextField()
    fill_color = models.TextField(null=True)
    stroke_color = models.TextField(null=True)
    png_image_file = models.ImageField(upload_to='svg-to-png-maps/')

    @property
    def url(self):
        return self.png_image_file.url

    @classmethod
    def get_png_image(cls, svg_path, fill_color=None, stroke_color=None):
        try:
            cache_key = (
                svg_path,
                cls._db_color(fill_color),
                cls._db_color(stroke_color)
            )
            return cache.get('svg_to_png_map')[cache_key].png_image_file
        except (KeyError, TypeError):
            try:
                tmp = cls.objects.get(
                    svg_path=svg_path,
                    fill_color=cls._db_color(fill_color),
                    stroke_color=cls._db_color(stroke_color)
                )
                return tmp.png_image_file
            except Exception as e:
                logger.info(f"PNG not found, file={svg_path}, exception: {e}")
                try:
                    return cls.create(
                        svg_path,
                        fill_color,
                        stroke_color
                    ).png_image_file
                except Exception as e:
                    logger.error(f"Failed to create SVG to PNG, file={svg_path}, exception: {e}")
                    return None

    @classmethod
    def create(cls, svg_path, fill_color=None, stroke_color=None):
        png_image = convert_svg_to_png_bytes(
            svg_path,
            fill_color=fill_color,
            stroke_color=stroke_color,
            width=32
        )
        return cls.objects.create(
            svg_path=svg_path,
            fill_color=cls._db_color(fill_color),
            stroke_color=cls._db_color(stroke_color),
            png_image_file=png_image
        )

    @classmethod
    def _db_color(cls, color):
        return color if color else ''

    def __str__(self):
        return f'(svg={self.svg_path}, fill={self.fill_color}, stroke={self.stroke_color}, png={self.png_image_file})'

    class Meta:
        unique_together = ('svg_path', 'fill_color', 'stroke_color')


class V1PageURLToV2PageMap(models.Model):
    v1_page_url = models.TextField()
    v2_page = models.ForeignKey(Page, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.v1_page_url} -> {self.v2_page.id}'

    @classmethod
    def create_map(cls, url, page):
        obj, __ = cls.objects.get_or_create(v2_page=page, defaults={'v1_page_url': url})

        return obj

    @classmethod
    def get_page_or_none(cls, v1_page_url):
        # See https://github.com/unicef/iogt/issues/850 for more details on why /home/ is prepended
        urls_to_match = [
            f'/home{v1_page_url}',
            f'/home{v1_page_url}/'
        ]
        obj = cls.objects.filter(v1_page_url__in=urls_to_match).first()
        return obj.v2_page if obj else None


class LocaleDetail(models.Model):
    is_active = models.BooleanField(
        default=True,
        help_text=_('When active locale will be shown in the language selector'))
    is_main_language = models.BooleanField(
        default=False,
        help_text=_('When active locale will be used as default language for the site'))

    locale = models.OneToOneField('wagtailcore.Locale', related_name='locale_detail', on_delete=models.CASCADE)

    def clean(self):
        if self.is_main_language and LocaleDetail.objects.filter(is_main_language=True).exclude(id=self.id).exists():
            raise ValidationError(_('There is already a main language for this site'))

    def __str__(self):
        return f'{self.locale}'
