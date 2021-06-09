from django.db import models
from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock

from questionnaires.forms import SurveysFormBuilder


class QuestionnairePage(Page):
    template = None

    parent_page_types = []
    subpage_types = []

    image = models.ForeignKey('wagtailimages.Image', on_delete=models.PROTECT, blank=True, null=True, related_name="survey_image")

    description = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.TextBlock()),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page', blocks.PageChooserBlock()),
    ], null=True, blank=True)
    thank_you_text = RichTextField(blank=True, null=True)
    thank_you_image = models.ForeignKey('wagtailimages.Image', on_delete=models.PROTECT, blank=True, null=True, related_name="survey_thank_you_image")
    thank_you_external_link = models.URLField(blank=True)
    thank_you_internal_link = models.CharField(blank=True, max_length=255)

    allow_anonymous_submissions = models.BooleanField(
        default=True,
        help_text='Check this to allow users who are NOT logged in to complete'
                  ' surveys.'
    )

    class Meta:
        abstract = True


class SurveyPage(QuestionnairePage):
    parent_page_types = ["home.HomePage", "home.Section", "home.Article"]
    form_builder = SurveysFormBuilder



