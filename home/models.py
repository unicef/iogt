import os

from django.conf import settings
from django.contrib.admin.utils import flatten
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
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
from comments.models import CommentableMixin
from iogt.views import check_user_session
from questionnaires.models import Survey, Poll, Quiz
from .blocks import (MediaBlock, SocialMediaLinkBlock,
                     SocialMediaShareButtonBlock,
                     EmbeddedQuestionnaireChooserBlock,
                     PageButtonBlock, ArticleChooserBlock)
from .forms import SectionPageForm
from .mixins import PageUtilsMixin
from .utils.progress_manager import ProgressManager

User = get_user_model()


class HomePage(Page):
    template = 'home/home_page.html'
    show_in_menus_default = True

    home_featured_content = StreamField([
        ('page_button', PageButtonBlock()),
        ('embedded_poll', EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Poll')),
        ('embedded_survey', EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Survey')),
        ('embedded_quiz', EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Quiz')),
        ('article', ArticleChooserBlock()),
    ], null=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            InlinePanel('home_page_banners', label=_("Home Page Banner")),
        ], heading=_('Home Page Banners')),
        StreamFieldPanel('home_featured_content')
    ]

    def get_context(self, request):
        check_user_session(request)
        context = super().get_context(request)
        context['banners'] = [
            home_page_banner.banner_page for home_page_banner in
            self.home_page_banners.filter(banner_page__live=True)
        ]
        context['featured_content'] = [
            featured_content.content for featured_content in
            self.featured_content.filter(content__live=True)
        ]
        context["footer"] = FooterPage.objects.live()
        return context


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
            return section_index_page.get_children().live()
        return cls.objects.none()


class Section(Page, PageUtilsMixin):
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

    tags = ClusterTaggableManager(through='SectionTaggedItem', blank=True)
    show_progress_bar = models.BooleanField(default=False)

    show_in_menus_default = True

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([FieldPanel("tags"), ], heading='Metadata'),
    ]

    content_panels = Page.content_panels + [
        ImageChooserPanel('lead_image'),
        SvgChooserPanel('icon'),
        FieldPanel('background_color'),
        FieldPanel('font_color'),
        MultiFieldPanel([
            InlinePanel('featured_content', max_num=1,
                        label=_("Featured Content")),
        ], heading=_('Featured Content')),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('show_progress_bar')
    ]

    base_form_class = SectionPageForm

    def get_descendant_articles(self):
        return Article.objects.descendant_of(self).exact_type(Article)

    def get_progress_bar_enabled_ancestor(self):
        return Section.objects.ancestor_of(self, inclusive=True).exact_type(
            Section).filter(
            show_progress_bar=True).first()

    def get_user_progress_dict(self, request):
        progress_manager = ProgressManager(request)
        read_article_count, total_article_count = progress_manager.get_progress(
            self)
        return {
            'read': read_article_count,
            'total': total_article_count
        }

    def get_context(self, request):
        check_user_session(request)
        context = super().get_context(request)
        context['featured_content'] = [
            featured_content.content for featured_content in
            self.featured_content.filter(content__live=True)
        ]
        context['sub_sections'] = self.get_children().live().type(Section)

        context['articles'] = self.get_children().live().type(Article)

        survey_page_ids = self.get_children().live().type(Survey).values_list('id', flat=True)
        context['surveys'] = Survey.objects.filter(pk__in=survey_page_ids)

        poll_page_ids = self.get_children().live().type(Poll).values_list('id', flat=True)
        context['polls'] = Poll.objects.filter(pk__in=poll_page_ids)

        quiz_page_ids = self.get_children().live().type(Quiz).values_list('id', flat=True)
        context['quizzes'] = Quiz.objects.filter(pk__in=quiz_page_ids)

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


class Article(Page, PageUtilsMixin, CommentableMixin):
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

    tags = ClusterTaggableManager(through='ArticleTaggedItem', blank=True)
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock(features=settings.WAGTAIL_RICH_TEXT_FIELD_FEATURES)),
        ('markdown', MarkdownBlock(icon='code')),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page_button', PageButtonBlock()),
        ('embedded_poll',
         EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Poll')),
        ('embedded_survey', EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Survey')),
        ('embedded_quiz', EmbeddedQuestionnaireChooserBlock(target_model='questionnaires.Quiz')),
        ('media', MediaBlock(icon='media')),
        ('chat_bot', ChatBotButtonBlock()),
    ])
    show_in_menus_default = True

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

    content_panels = Page.content_panels + [
        ImageChooserPanel('lead_image'),
        SvgChooserPanel('icon'),
        StreamFieldPanel('body'),
        MultiFieldPanel([
            InlinePanel('recommended_articles',
                        label=_("Recommended Articles")),
        ],
            heading='Recommended Content')
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([FieldPanel("tags"), ], heading='Metadata'),
    ]

    search_fields = [
        index.SearchField('get_heading_values', partial_match=True, boost=1),
        index.SearchField('get_paragraph_values', partial_match=True),
        index.SearchField('title', partial_match=True, boost=2),

        index.FilterField('live')
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(promote_panels, heading='Promote'),
        ObjectList(Page.settings_panels, heading='Settings'),
        ObjectList(CommentableMixin.comments_panels, heading='Comments')
    ])

    def _get_progress_enabled_section(self):
        """
        Returning .first() will bypass any discrepancies in settings show_progress_bar=True
        for sections
        :return:
        """
        return Section.objects.ancestor_of(self).type(Section).filter(
            show_progress_bar=True).first()

    def get_context(self, request):
        check_user_session(request)
        context = super().get_context(request)
        context['breadcrumbs'] = [crumb for crumb in self.get_ancestors() if
                                  not crumb.is_root()]
        context['sections'] = self.get_ancestors().type(Section)

        progress_enabled_section = self._get_progress_enabled_section()

        if progress_enabled_section:
            context.update({
                'user_progress': progress_enabled_section.get_user_progress_dict(
                    request)
            })

        return context

    def serve(self, request):
        response = super().serve(request)
        if response.status_code == status.HTTP_200_OK:
            User.record_article_read(request=request, article=self)
        return response

    def description(self):
        for block in self.body:
            if block.block_type == 'paragraph':
                return block
        return ''

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")



class BannerIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.BannerPage']


class BannerPage(Page):
    parent_page_types = ['home.BannerIndexPage']
    subpage_types = []

    banner_description = RichTextField(null=True, blank=True)

    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        on_delete=models.PROTECT,
        null=True, blank=True,
        help_text=_('Image to display as the banner')
    )
    banner_background_image = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        null=True, blank=True,
        on_delete=models.PROTECT,
        help_text=_('Background image')
    )

    banner_link_page = models.ForeignKey(
        Page, null=True, blank=True, related_name='banners',
        on_delete=models.PROTECT,
        help_text=_('Optional page to which the banner will link to'))

    banner_button_text = models.CharField(
        null=True, blank=True,
        max_length=35,
        help_text=_('The title for a button')
    )
    banner_icon_button = models.ForeignKey(
        'wagtailimages.Image',
        related_name='+',
        on_delete=models.PROTECT,
        null=True, blank=True,
        help_text=_('Icon Button')
    )
    align_center = BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel('banner_description'),
        ImageChooserPanel('banner_image'),
        #ImageChooserPanel('banner_background_image'),
        PageChooserPanel('banner_link_page'),
        #FieldPanel('banner_button_text'),
        #ImageChooserPanel('banner_icon_button'),
        #FieldPanel('align_center')
    ]


class FooterIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['home.FooterPage']

    def __str__(self):
        return self.title


class FooterPage(Article):
    parent_page_types = ['home.FooterIndexPage']
    subpage_types = []
    template = 'home/article.html'

    @classmethod
    def get_active_footers(cls):
        return cls.objects.filter(locale=Locale.get_active()).live()


@register_setting
class SiteSettings(BaseSetting):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
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

    panels = [
        ImageChooserPanel('logo'),
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


@register_setting
class CacheSettings(BaseSetting):
    cache = models.BooleanField(
        default=True,
        verbose_name=_("Prompt users to download?"),
        help_text=_(
            "check to prompt first time users to download the website as an app"),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('cache'),
            ],
            heading="Cache settings",
        )
    ]

    class Meta:
        verbose_name = "Cache settings"


class IogtFlatMenuItem(AbstractFlatMenuItem):
    menu = ParentalKey(
        'wagtailmenus.FlatMenu',
        on_delete=models.CASCADE,
        related_name="iogt_flat_menu_items",
    )
    icon = models.ForeignKey(
        Svg,
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    color = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    color_text = models.CharField(
        max_length=6,
        blank=True,
        null=True
    )

    panels = AbstractFlatMenuItem.panels + [
        SvgChooserPanel('icon'),
        FieldPanel('color'),
        FieldPanel('color_text')
    ]


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
        help_text=_("Provide name"),
    )
    short_name = models.CharField(
        max_length=255,
        verbose_name=_("Short name"),
        help_text=_("Provide short name"),
    )
    scope = models.CharField(
        max_length=255,
        verbose_name=_("Scope"),
        help_text=_("Provide scope"),
    )
    start_url = models.CharField(
        max_length=255,
        verbose_name=_("Start URL"),
        help_text=_("Provide start URL"),
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
        help_text=_("Provide browser UI"),
    )
    background_color = models.CharField(
        max_length=10,
        verbose_name=_("Background color"),
        help_text=_("Provide background color (example: #FFF)"),
    )
    theme_color = models.CharField(
        max_length=10,
        verbose_name=_("Theme color"),
        help_text=_("Provide theme color(example: #493174)"),
    )
    description = models.CharField(
        max_length=500,
        verbose_name=_("Description"),
        help_text=_("Provide description"),
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
    icon_196_196 = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
        verbose_name=_("Icon 196x196 (maskable)"),
        help_text=_(
            "Add PNG icon 196x196 px (maskable image can be created using https://maskable.app/)"
        ),
        validators=[ImageValidator(width=196, height=196)],
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
                ImageChooserPanel("icon_196_196"),
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
