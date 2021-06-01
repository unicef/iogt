from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey

from wagtail.core import blocks
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel, MultiFieldPanel, PageChooserPanel, InlinePanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.core.rich_text import get_text_for_indexing
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class HomePage(Page):
    template = 'home/section.html'

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            InlinePanel('page_banners', label=_("Banners")),
        ], heading='Banners'),
        MultiFieldPanel([
            InlinePanel('featured_content', label=_("Featured Content")),
        ], heading='Featured Content'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = self.get_descendants().type(Article)
        context['featured_content'] = [featured_content.content for featured_content in self.featured_content.all()]
        context['banners'] = [page_banner.banner for page_banner in self.page_banners.all()]
        return context


class FeaturedContent(Orderable):
    source = ParentalKey('HomePage', related_name='featured_content', on_delete=models.CASCADE, blank=True)
    content = models.ForeignKey(Page, on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('content'),
    ]


class Section(Page):
    icon = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    icon_active = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True,
    )
    color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
    )
    show_in_menus_default = True

    content_panels = Page.content_panels + [
        ImageChooserPanel('icon'),
        ImageChooserPanel('icon_active'),
        FieldPanel('color'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = self.get_children().type(Article)
        return context


class Article(Page):
    lead_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page', blocks.PageChooserBlock()),
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
        StreamFieldPanel('body')
    ]

    search_fields = [
        index.SearchField('get_heading_values', partial_match=True, boost=1),
        index.SearchField('get_paragraph_values', partial_match=True),
        index.SearchField('title', partial_match=True, boost=2),

        index.FilterField('live')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['breadcrumbs'] = [crumb for crumb in self.get_ancestors() if not crumb.is_root()]
        context['sections'] = self.get_ancestors().type(Section)
        return context

    def description(self):
        for block in self.body:
            if block.block_type == 'paragraph':
                return block
        return ''


@register_snippet
class Banner(models.Model):
    title = models.CharField(max_length=255)
    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    banner_link_page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL)
    external_link = models.URLField(null=True, blank=True)

    panels = [
        FieldPanel('title'),
        ImageChooserPanel('banner_image'),
        PageChooserPanel('banner_link_page'),
        FieldPanel('external_link'),
    ]

    def __str__(self):
        return self.title


class PageBanner(Orderable):
    source = ParentalKey(Page, related_name='page_banners', on_delete=models.CASCADE, null=True, blank=True)
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE)

    panels = [
        SnippetChooserPanel('banner'),
    ]


@register_snippet
class Footer(models.Model):
    title = models.CharField(max_length=255)
    logos = StreamField([
        ('image', ImageChooserBlock(required=False))
    ], blank=True)
    navigation = StreamField([
        ('link_group', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('links', blocks.StreamBlock([
                ('page', blocks.PageChooserBlock())
            ]))
        ], required=False))
    ], blank=True)
    essential = StreamField([
        ('page', blocks.PageChooserBlock()),
    ])

    panels = [
        FieldPanel('title'),
        StreamFieldPanel('logos'),
        StreamFieldPanel('navigation'),
        StreamFieldPanel('essential'),
    ]

    def __str__(self):
        return self.title
