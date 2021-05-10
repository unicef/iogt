from django.db import models

from django.utils.encoding import force_str

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from wagtail.core import blocks
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import StreamField

from wagtail.core.rich_text import get_text_for_indexing

from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from wagtail.admin import widgets
from wagtail.search import index
from django.utils import timezone



class HomePage(Page):
    template = 'home/section.html'

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = self.get_descendants().type(Article)
        return context


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
        StreamFieldPanel('body'),
        InlinePanel('comment', label="Comments"),
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
    
    def get_comments(self):
        return self.comment.filter(is_approved=True, is_removed=False)


@register_snippet
class Comment(index.Indexed, Orderable):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="comments",
        on_delete=models.SET_NULL
    )
    page = ParentalKey('wagtailcore.Page', related_name='comment')
    author_website = models.URLField(_("author's Website"), blank=True)
    comment = models.TextField(_('comment'), max_length=3000)

    # Metadata
    submitted_at = models.DateTimeField(
        _('date/time submitted'),
        default=None,
        db_index=True
    )
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    is_approved = models.BooleanField(
        _('is approved'),
        default=True,
    )
    is_removed = models.BooleanField(
        _('is removed'),
        default=False,
        db_index=True,
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    date_widget = widgets.AdminDateInput(
        attrs = {
            'placeholder': 'dd-mm-yyyy'
        }
    )

    panels = [
        # SnippetChooserPanel('author'),
        FieldPanel('author'),
        PageChooserPanel('page'),
        FieldPanel('author_website'),
        FieldPanel('comment'),
        FieldPanel('submitted_at', widget=date_widget),
        FieldPanel('is_approved'),
        FieldPanel('is_removed'),
        FieldPanel('ip_address'),
        SnippetChooserPanel('parent'),

    ]

    search_fields = [
        index.SearchField('comment', partial_match=True),
    ]

    def save(self, *args, **kwargs):
        if self.submitted_at is None:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.comment

    def is_parent(self):
        return self.parent

    def get_replies(self):
        return self.replies.filter(is_approved=True, is_removed=False)

@register_snippet
class FlagComment(index.Indexed, models.Model):
    flagger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('flagger'),
        on_delete=models.CASCADE,
        related_name="comment_flags",
    )
    comment = models.ForeignKey(
        Comment,
        verbose_name=_('comment'),
        on_delete=models.CASCADE,
        related_name="comment_flags",
    )
    flag = models.CharField( # Can be enum from client side
        _('flag'),
        max_length=30,
        db_index=True
    )
    flagged_at = models.DateTimeField(_('flag date time'), default=None)

    date_widget = widgets.AdminDateInput(
        attrs = {
            'placeholder': 'dd-mm-yyyy'
        }
    )

    panels = [
        FieldPanel('flagger'),
        SnippetChooserPanel('comment'),
        FieldPanel('flag'),
        FieldPanel('flagged_at', widget=date_widget),
    ]

    search_fields = [
        index.SearchField('comment', partial_match=True),
    ]

    class Meta:
        unique_together = [('flagger', 'comment', 'flag')]
        verbose_name = _('comment flag')
        verbose_name_plural = _('comment flags')

    def __str__(self):
        return self.flag

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
