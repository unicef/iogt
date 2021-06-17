import json

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from home.blocks import MediaBlock
from home.models import HomePage
from iogt.settings import base
from iogt_users.models import User
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (FieldPanel, InlinePanel,
                                         MultiFieldPanel, StreamFieldPanel)
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.models import (AbstractForm, AbstractFormField,
                                          AbstractFormSubmission)
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock


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
    allow_anonymous_submissions = models.BooleanField(
        default=True,
        help_text=_(
            "Check this to allow users who are NOT logged in to complete surveys."
        ),
    )

    allow_multiple_submissions = models.BooleanField(
        default=True,
        help_text=_("Check this to allow multiple form submissions for users"),
    )
    submit_button_text = models.CharField(
        max_length=40, null=True, default="Submit", help_text=_("Submit button text")
    )

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


class Poll(QuestionnairePage):
    template = "poll/poll.html"
    parent_page_types = ["home.HomePage", "home.Section", "home.Article"]
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
    page = ParentalKey("Survey", on_delete=models.CASCADE, related_name="form_fields")


class Survey(QuestionnairePage, AbstractForm):
    parent_page_types = ["home.HomePage", "home.Section", "home.Article"]
    template = "survey/survey.html"
    multi_step = models.BooleanField(
        default=False,
        verbose_name="Multi-step",
        help_text="Whether to display the survey questions to the user one at"
        " a time, instead of all at once.",
    )

    content_panels = Page.content_panels + [
        FormSubmissionsPanel(),
        MultiFieldPanel(
            [
                FieldPanel("allow_anonymous_submissions"),
                FieldPanel("allow_multiple_submissions"),
                FieldPanel("submit_button_text"),
                FieldPanel("multi_step"),
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
        InlinePanel("form_fields", label="Form fields"),
    ]

    def get_submission_class(self):
        return SurveySubmission

    def process_form_submission(self, form):
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self,
            user=form.user,
        )

    def serve(self, request, *args, **kwargs):
        if (
            not self.allow_multiple_submissions
            and self.get_submission_class()
            .objects.filter(page=self, user__pk=request.user.pk)
            .exists()
        ):
            return render(request, self.template, self.get_context(request))
        if self.multi_step:
            return self.serve_questions_separately(request)

        return super().serve(request, *args, **kwargs)

    def serve_questions_separately(self, request, *args, **kwargs):
        session_key_data = "form_data-%s" % self.pk
        is_last_step = False
        step_number = request.GET.get("p", 1)

        paginator = Paginator(self.get_form_fields(), per_page=1)
        try:
            step = paginator.page(step_number)
        except PageNotAnInteger:
            step = paginator.page(1)
        except EmptyPage:
            step = paginator.page(paginator.num_pages)
            is_last_step = True

        if request.method == "POST":
            # The first step will be submitted with step_number == 2,
            # so we need to get a form from previous step
            # Edge case - submission of the last step
            prev_step = (
                step if is_last_step else paginator.page(step.previous_page_number())
            )

            # Create a form only for submitted step
            prev_form_class = self.get_form_class_for_step(prev_step)
            prev_form = prev_form_class(request.POST, page=self, user=request.user)
            if prev_form.is_valid():
                # If data for step is valid, update the session
                form_data = request.session.get(session_key_data, {})
                form_data.update(prev_form.cleaned_data)
                request.session[session_key_data] = form_data

                if prev_step.has_next():
                    # Create a new form for a following step, if the following step is present
                    form_class = self.get_form_class_for_step(step)
                    form = form_class(page=self, user=request.user)
                else:
                    # If there is no next step, create form for all fields
                    form = self.get_form(
                        request.session[session_key_data], page=self, user=request.user
                    )

                    if form.is_valid():
                        # Perform validation again for whole form.
                        # After successful validation, save data into DB,
                        # and remove from the session.
                        form_submission = self.process_form_submission(form)
                        del request.session[session_key_data]
                        # render the landing page
                        return self.render_landing_page(
                            request, form_submission, *args, **kwargs
                        )
            else:
                # If data for step is invalid
                # we will need to display form again with errors,
                # so restore previous state.
                form = prev_form
                step = prev_step
        else:
            # Create empty form for non-POST requests
            form_class = self.get_form_class_for_step(step)
            form = form_class(page=self, user=request.user)

        context = self.get_context(request)
        context["form"] = form
        context["fields_step"] = step
        return render(request, self.template, context)

    class Meta:
        verbose_name = "survey"
        verbose_name_plural = "surveys"


class SurveySubmission(AbstractFormSubmission):
    user = models.ForeignKey(
        base.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )

    def get_data(self):
        form_data = super().get_data()
        form_data.update(
            {
                "user": self.user if self.user else None,
            }
        )
        return form_data
