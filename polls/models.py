from django.db import models
from django.utils.translation import ugettext_lazy as _
from home.models import Article
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.core.models import Page


class Question(Page):
    template = "polls/question.html"
    subpage_types = []  # todo add subpages
    parent_page_types = [
        "home.HomePage",
    ]

    """
    the option of sitting either within a parent section or sub-section or as a child to an article.
    The option to have a click-button to begin or direct display (either onto the body of the article as an optional content module or in the parent section or sub-section) should be available.
    the option to require login or accept anonymous responses
    the option to allow multiple responses per user or not
    the ability to format the confirmation page to include text ,images, media, and links as an article.
    """

    show_results = models.BooleanField(
        default=True, help_text=_("This option allows the users to see the results.")
    )
    randomise_options = models.BooleanField(
        default=False,
        help_text=_(
            "Randomising the options allows the options to be shown in a different order each time the page is displayed."
        ),
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
    is_login_required = models.BooleanField(
        default=False, help_text=_("Allows not logged in to vote?")
    )

    confirmation_text = models.CharField(max_length=200, null=True, blank=True)
    confirmation_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Add image to result page",
    )
    # confirmation_media
    internal_link = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="If selected, this url will be used first",
    )
    external_url = models.URLField(
        blank=True,
        null=True,
        help_text="If added, this url will be used secondarily",
    )
    confirmation_link_text = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        default="Check more",
        help_text="Text to be linked",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("is_login_required"),
                FieldPanel("show_results"),
                FieldPanel("randomise_options"),
                FieldPanel("result_as_percentage"),
                FieldPanel("allow_multiple_choice"),
            ],
            heading=_(
                "Question Settings",
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("confirmation_text"),
                FieldPanel("confirmation_image"),
                FieldPanel("internal_link"),
                FieldPanel("external_url"),
                FieldPanel("confirmation_link_text"),
                FieldPanel("confirmation_image"),
            ],
            heading="Thank you page settings",
        ),
    ]

    def url(self):
        internal_link = self.internal_link
        external_url = self.external_url
        if internal_link:
            return internal_link.url
        elif external_url:
            return external_url

        return None

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class
