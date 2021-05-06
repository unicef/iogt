from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from wagtail.core import blocks
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
from wagtail.admin import widgets



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

    content_panels = Page.content_panels + [
        ImageChooserPanel('lead_image'),
        StreamFieldPanel('body'),
        InlinePanel('comment', label="Comments"),
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
class Comment(Orderable):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="comments",
        on_delete=models.SET_NULL
    )
    page = ParentalKey('Article', related_name='comment')
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

    ]


    def __str__(self):
        return self.comment

@register_snippet
class FlagComment(models.Model):
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
