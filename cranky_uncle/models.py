import requests
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from home.mixins import PageUtilsMixin, TitleIconMixin


class CrankyUncleChannel(models.Model):
    display_name = models.CharField(
        max_length=80,
        help_text=_('Name for the cranky uncle bot that the user will seen when interacting with it'),
    )
    request_url = models.URLField(
        max_length=200,
        help_text=_('To set up a cranky uncle bot channel on your RapidPro server and get a request URL, '
                    'follow the steps outline in the Section "Setting up a Chatbot channel" '
                    'here: https://github.com/unicef/iogt/blob/develop/messaging/README.md'),
    )

    # Plan on adding trigger words

    def __str__(self):
        return f"{self.display_name}, {self.request_url}"


# class CrankyUncle(Page, PageUtilsMixin, TitleIconMixin):
#     from .blocks import CrankyUncleButtonBlock
#
#     lead_image = models.ForeignKey(
#         'wagtailimages.Image',
#         on_delete=models.PROTECT,
#         related_name='+',
#         blank=True,
#         null=True,
#     )
#     body = StreamField(
#         [
#             ('cranky_uncle_bot', CrankyUncleButtonBlock()),
#         ],
#         null=True,
#         blank=True,
#     )
#
#     show_in_menus_default = True
#
#     parent_page_types = ['home.HomePage', 'home.Section', 'home.FooterIndexPage']
#     subpage_types = []
#
#     content_panels = Page.content_panels + [
#         ImageChooserPanel('lead_image'),
#         StreamFieldPanel('body'),
#     ]
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name = _("Cranky")
#         verbose_name_plural = _("Cranky Uncle")


class CrankyUncle(Page, PageUtilsMixin, TitleIconMixin):
    parent_page_types = [
        "home.HomePage", "home.Section", 'home.FooterIndexPage'
    ]
    subpage_types = []
    # template = 'cranky/cranky_index_page.html'
    # show_in_menus_default = True

    button_text = models.CharField(max_length=255, null=True, blank=True)
    trigger_string = models.CharField(max_length=255, null=True, blank=True)
    channel = models.ForeignKey(
        CrankyUncleChannel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('button_text'),
        FieldPanel('trigger_string'),

        FieldPanel('channel'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Cranky")
        verbose_name_plural = _("Cranky Uncle")


class CrankyUncleIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['cranky_uncle.CrankyUncle']


class RapidPro(models.Model):
    rapidpro_id = models.AutoField(primary_key=True)
    text = models.TextField()
    quick_replies = models.JSONField(null=True, blank=True)
    to = models.CharField(max_length=255)
    from_field = models.CharField(max_length=255)  # 'from' is a reserved keyword, so using 'from_field'
    channel = models.CharField(max_length=255)
    flow_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'RapidPro {self.rapidpro_id}'
