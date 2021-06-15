import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.models import AbstractForm, AbstractFormField, AbstractFormSubmission

from home.blocks import MediaBlock
from home.models import HomePage
from iogt.settings import base
from iogt.views import create_final_external_link
from iogt_users.models import User
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel, InlinePanel,
)
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock

# from questionnaires.forms import SurveysFormBuilder


class QuestionnairePage(Page):
    template = None
    parent_page_types = []
    subpage_types = []

    description = StreamField(
        [
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        null=True,
        blank=True,
    )
    thank_you_text = StreamField(
        [
            ("paragraph", blocks.RichTextBlock()),
            ("media", MediaBlock(icon="media")),
            ("image", ImageChooserBlock()),
        ],
        null=True,
        blank=True,
    )
    thank_you_link_text = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        default="Check more",
        help_text=_("Text to be linked"),
    )
    thank_you_external_link = models.URLField(
        null=True,
        blank=True,
        help_text=_(
            "Optional external link to which user after questions can go "
            "e.g., https://www.google.com"
        ),
    )
    thank_you_internal_link = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_related",
        on_delete=models.PROTECT,
        help_text=_("Optional page to which user after questions can go"),
    )
    allow_anonymous_submissions = models.BooleanField(
        default=True,
        help_text=_(
            "Check this to allow users who are NOT logged in to complete surveys."
        ),
    )
    # TODO create validation if set to false
    allow_multiple_submissions = models.BooleanField(
        default=True,
        help_text=_("Check this to allow multiple form submissions for users")
    )

    start_button_required = models.BooleanField(
        default=False,
        help_text=_("Check this to demand clicking start before showing questionnaire options")
    )
    start_button_text = models.CharField(max_length=40, null=True, default="Start", help_text=_("Start button text"))
    submit_button_text = models.CharField(max_length=40, null=True, default="Submit", help_text=_("Submit button text"))

    @property
    def thank_you_link(self):
        if self.thank_you_internal_link:
            return self.thank_you_internal_link.url
        if self.thank_you_external_link:
            return create_final_external_link(self.thank_you_external_link)
        else:
            return "#"

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class PollIndexPage(Page):
    parent_page_types = ["home.HomePage", "home.Section", "home.Article"]
    subpage_types = ["questionnaires.Poll"]


class Poll(QuestionnairePage):
    template = "poll/poll.html"
    parent_page_types = [
        "questionnaires.PollIndexPage",
    ]
    subpage_types = ["questionnaires.Choice"]

    show_results = models.BooleanField(
        default=True, help_text=_("This option allows the users to see the results.")
    )
    result_as_percentage = models.BooleanField(
        default=True,
        help_text=_(
            "If not checked, the results will be shown as a total instead of a percentage."
        ),
    )
    allow_multiple_choice = models.BooleanField(
        default=False, help_text=_("Allows the user to choose more than one option.")
    )
    randomise_options = models.BooleanField(
        default=False,
        help_text=_(
            "Randomising the options allows the options to be shown in a different "
            "order each time the page is displayed."
        ),
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("allow_anonymous_submissions"),
                FieldPanel("show_results"),
                FieldPanel("randomise_options"),
                FieldPanel("result_as_percentage"),
                FieldPanel("allow_multiple_choice"),
                FieldPanel("allow_multiple_submissions"),
                FieldPanel("start_button_required"),
                FieldPanel("start_button_text"),
                FieldPanel("submit_button_text"),
            ],
            heading=_(
                "General settings for poll",
            ),
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel("description"),
            ],
            heading=_(
                "Description at poll page",
            ),
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel("thank_you_text"),
            ],
            heading="Description at thank you page",
        ),
        MultiFieldPanel(
            [
                FieldPanel("thank_you_link_text"),
                PageChooserPanel("thank_you_internal_link"),
                FieldPanel("thank_you_external_link"),
            ],
            heading="Link at  thank you page",
        ),
    ]

    def choices(self):
        if self.randomise_options:
            return Choice.objects.live().child_of(self).order_by("?")
        return Choice.objects.live().child_of(self)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["choices"] = self.choices
        return context

    class Meta:
        verbose_name = "Poll"
        verbose_name_plural = "Polls"


class Choice(Page):
    parent_page_types = ["questionnaires.Poll"]
    subpage_types = []

    votes = models.IntegerField(default=0)
    choice_votes = models.ManyToManyField(
        "ChoiceVote", related_name="choices", blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"


class ChoiceVote(models.Model):
    user = models.ForeignKey(
        User,
        related_name="choice_votes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    choice = models.ManyToManyField(Choice, blank=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)
    submission_date = models.DateField(null=True, blank=True, auto_now_add=True)

    @property
    def answer(self):
        return ",".join([c.title for c in self.choice.all()])


class SurveyFormField(AbstractFormField):
    page = ParentalKey('Survey', on_delete=models.CASCADE, related_name='form_fields')


class Survey(QuestionnairePage, AbstractForm):
    parent_page_types = ["home.HomePage", "home.Section", "home.Article"]
    template = "survey/survey.html"

    FormSubmissionsPanel(),

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("allow_anonymous_submissions"),
                FieldPanel("allow_multiple_submissions"),
                FieldPanel("start_button_required"),
                FieldPanel("start_button_text"),
                FieldPanel("submit_button_text"),
            ],
            heading=_(
                "General settings for survey",
            ),
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel("description"),
            ],
            heading=_(
                "Description at survey page",
            ),
        ),
        MultiFieldPanel(
            [
                StreamFieldPanel("thank_you_text"),
            ],
            heading="Description at thank you page",
        ),
        MultiFieldPanel(
            [
                FieldPanel("thank_you_link_text"),
                PageChooserPanel("thank_you_internal_link"),
                FieldPanel("thank_you_external_link"),
            ],
            heading="Link at  thank you page",
        ),
        InlinePanel('form_fields', label="Form fields"),
    ]

    def get_submission_class(self):
        return SurveySubmission

    def process_form_submission(self, form):
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self, user=form.user
        )

    class Meta:
        verbose_name = "survey"
        verbose_name_plural = "surveys"


class SurveySubmission(AbstractFormSubmission):
    user = models.ForeignKey(base.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

