from django.db import models

from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock


class HomePage(Page):
    pass

class Section(Page):
    pass

class Article(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page', blocks.PageChooserBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body')
    ]
