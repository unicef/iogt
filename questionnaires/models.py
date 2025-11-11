from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property

from django.core.paginator import EmptyPage, PageNotAnInteger
from django.db import models
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from wagtail_localize.fields import TranslatableField
from wagtailmarkdown.blocks import MarkdownBlock
from wagtailsvg.edit_handlers import SvgChooserPanel
from wagtailsvg.models import Svg
from wagtail.models import Orderable, ClusterableModel
from user_notifications.models import NotificationTag
from django.db.models import Avg

from home.blocks import (
    MediaBlock,
    NumberedListBlock,
    PageButtonBlock,
    RawHTMLBlock,
    DownloadButtonBlock,
)
from home.mixins import PageUtilsMixin, TitleIconMixin
from home.utils import (
    collect_urls_from_streamfield,
    get_all_renditions_urls,
)
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import (FieldPanel, InlinePanel, MultiFieldPanel)
from wagtail.contrib.forms.models import (AbstractForm, AbstractFormField,
                                          AbstractFormSubmission)
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.images.blocks import ImageChooserBlock

from questionnaires.blocks import SkipState, SkipLogicField
from questionnaires.edit_handlers import FormSubmissionsPanel
from questionnaires.forms import CustomFormBuilder, SurveyForm, QuizForm
from questionnaires.utils import SkipLogicPaginator, FormHelper


FORM_FIELD_CHOICES = (
    ('checkbox', _('Checkbox')),
    ('checkboxes', _('Checkboxes')),
    ('date', _('Date')),
    ('datetime', _('Date/time')),
    ('dropdown', _('Drop down')),
    ('email', _('Email')),
    ('singleline', _('Single line text')),
    ('multiline', _('Multi-line text')),
    ('number', _('Number')),
    ('positivenumber', _('Positive number')),
    ('radio', _('Radio buttons')),
    ('url', _('URL')),
)


class QuestionnairePage(Page, PageUtilsMixin, TitleIconMixin):
    template = None
    parent_page_types = []
    subpage_types = []
    show_in_menus_default = True

    description = StreamField(
        [
            ('heading', blocks.CharBlock(form_classname="full title", template='blocks/heading.html')),
            ('paragraph', blocks.RichTextBlock(features=settings.WAGTAIL_RICH_TEXT_FIELD_FEATURES)),
            ('paragraph_v1_legacy', RawHTMLBlock(icon='code')),
            ("image", ImageChooserBlock(template='blocks/image.html')),
            ('list', MarkdownBlock(icon='code')),
            ('numbered_list', NumberedListBlock(MarkdownBlock(icon='code'))),
            ('page_button', PageButtonBlock()),
            ('download', DownloadButtonBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    thank_you_text = StreamField(
        [
            ("paragraph", blocks.RichTextBlock(features=settings.WAGTAIL_RICH_TEXT_FIELD_FEATURES)),
            ("media", MediaBlock(icon="media")),
            ("image", ImageChooserBlock(template='blocks/image.html')),
        ],
        null=True,
        blank=True,
        use_json_field=True,
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
        max_length=40, null=True, default=_("Submit"), help_text=_("Submit button text")
    )

    direct_display = models.BooleanField(default=False)

    index_page_description = models.TextField(null=True, blank=True)
    index_page_description_line_2 = models.TextField(null=True, blank=True)

    terms_and_conditions = StreamField(
        [
            ("paragraph", blocks.RichTextBlock(features=settings.WAGTAIL_RICH_TEXT_FIELD_FEATURES)),
            ('page_button', PageButtonBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    icon = models.ForeignKey(
        Svg,
        related_name='+',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    image_icon = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )

    settings_panels = Page.settings_panels + [
        FieldPanel('direct_display')
    ]

    def __str__(self):
        return self.title

    def serve(self, request, *args, **kwargs):
        if request.session.session_key is None:
            request.session.save()
        self.session = request.session

        multiple_submission_filter = (
            Q(session_key=request.session.session_key) if request.user.is_anonymous else Q(user__pk=request.user.pk)
        )
        multiple_submission_check = (
            not self.allow_multiple_submissions
            and self.get_submission_class().objects.filter(multiple_submission_filter, page=self).exists()
        )
        anonymous_user_submission_check = request.user.is_anonymous and not self.allow_anonymous_submissions
        if multiple_submission_check or anonymous_user_submission_check:
            return render(request, self.template, self.get_context(request))

        if hasattr(self, "multi_step") and self.multi_step and self.get_form_fields():
            return self.serve_questions_separately(request)

        return super().serve(request, *args, **kwargs)

    def serve_questions_separately(self, request, *args, **kwargs):
        form_helper = FormHelper(pk=self.pk, request=request)
        is_last_step = False
        step_number = request.GET.get("p", 1)

        form_data = form_helper.get_form_data()

        paginator = SkipLogicPaginator(
            self.get_form_fields(),
            request.POST,
            form_data,
        )

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
            try:
                prev_step = (
                    step if is_last_step else paginator.page(int(step_number) - 1)
                )
            except EmptyPage:
                prev_step = step
                step = paginator.page(prev_step.next_page_number())

            # Create a form only for submitted step
            prev_form_class = self.get_form_class_for_step(prev_step)
            prev_form = prev_form_class(
                paginator.new_answers,
                page=self,
                user=request.user
            )
            if prev_form.is_valid():
                # If data for step is valid, update the session
                form_data = form_helper.get_form_data()
                form_data.update(prev_form.cleaned_data)
                form_helper.set_form_data(form_data)

                if prev_step.has_next():
                    # Create a new form for a following step, if the following step is present
                    form_class = self.get_form_class_for_step(step)
                    form = form_class(page=self, user=request.user)
                else:
                    # If there is no next step, create form for all fields
                    form = self.get_form(
                        form_helper.get_form_data(),
                        page=self, user=request.user
                    )

                    if form.is_valid():
                        # Perform validation again for whole form.
                        # After successful validation, save data into DB,
                        # and remove from the session.
                        form_submission = self.process_form_submission(form)
                        form_helper.set_full_form_data()
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

    def process_form_submission(self, form):
        user = form.user
        self.get_submission_class().objects.create(
            form_data=form.cleaned_data,
            page=self,
            user=None if user.is_anonymous else user,
            session_key=self.session.session_key,
        )

    # Required by Wagtail Forms
    def get_submissions_list_view_class(self):
        from questionnaires.views import CustomSubmissionsListView
        return CustomSubmissionsListView

    def get_export_filename(self):
        object_type = self.__class__.__name__.lower()
        title = self.title
        timestamp = timezone.now().strftime(settings.EXPORT_FILENAME_TIMESTAMP_FORMAT)

        return f'{object_type}-{title}_{timestamp}'

    def get_data_fields(self):
        data_fields = [
            ('user', _('User')),
            ('submit_time', _('Submission Date')),
            ('page_url', _('Page URL')),
        ]
        data_fields += [
            (field.clean_name, field.admin_label or field.label)
            for field in self.get_form_fields()
        ]
        return data_fields

    @property
    def offline_urls(self):
        urls = (
            [self.url]
            + collect_urls_from_streamfield(self.description)
            + collect_urls_from_streamfield(self.thank_you_text)
        )

        if self.image_icon:
            urls += get_all_renditions_urls(self.image_icon)

        return urls

    def get_submit_button_text(self, fields_step=None):
        submit_button_text = self.submit_button_text
        if fields_step and fields_step.paginator.num_pages != fields_step.number:
            submit_button_text = _("Next")

        return submit_button_text

    class Meta:
        abstract = True


class SurveyFormField(AbstractFormField):
    page = ParentalKey("Survey", on_delete=models.CASCADE, related_name="survey_form_fields")
    clean_name = models.TextField(
        verbose_name=_('name'),
        blank=True,
        default='',
        help_text=_('Safe name of the form field, the label converted to ascii_snake_case. '
                    'This will appear in the HTML but will not be visible to the user')
    )
    label = models.TextField(
        verbose_name=_('label'),
        help_text=_('The label of the form field')
    )
    field_type = models.CharField(
        verbose_name=_('field type'),
        max_length=16,
        choices=FORM_FIELD_CHOICES
    )
    admin_label = models.CharField(
        verbose_name=_('admin_label'),
        max_length=256,
        help_text=_('Column header used during CSV export of survey '
                    'responses.'),
    )
    skip_logic = SkipLogicField(null=True, blank=True)
    default_value = models.TextField(
        verbose_name=_('default value'),
        blank=True,
        help_text=_('Default value. Pipe (|) separated values supported for checkboxes.')
    )
    page_break = models.BooleanField(
        default=False,
        help_text=_(
            'Inserts a page break which puts the next question onto a new page'
        )
    )
    panels = [
        FieldPanel('label'),
        FieldPanel('clean_name', classname='disabled-clean-name'),
        FieldPanel('help_text'),
        FieldPanel('required'),
        FieldPanel('field_type', classname="formbuilder-type"),
        FieldPanel('skip_logic', classname='skip-logic'),
        FieldPanel('default_value', classname="formbuilder-default"),
        FieldPanel('admin_label'),
        FieldPanel('page_break'),
    ]

    @property
    def has_skipping(self):
        return any(
            logic.value['skip_logic'] != SkipState.NEXT
            for logic in self.skip_logic
        )

    def choice_index(self, choice):
        if self.field_type == 'checkbox':
            choice = 'true' if choice == 'on' else 'false'
        try:
            return self.choices.split('|').index(choice)
        except ValueError:
            pass

        return None

    def next_action(self, choice):
        choice_index = self.choice_index(choice)
        if choice_index is None:
            return SkipState.NEXT
        return self.skip_logic[choice_index].value['skip_logic']

    def is_next_action(self, choice, *actions):
        if self.has_skipping:
            return self.next_action(choice) in actions
        return False

    def next_page(self, choice):
        logic = self.skip_logic[self.choice_index(choice)]
        return logic.value[self.next_action(choice)]


class Survey(QuestionnairePage, AbstractForm):
    base_form_class = SurveyForm
    form_builder = CustomFormBuilder
    notification_tags = ParentalManyToManyField(NotificationTag, blank=True)

    parent_page_types = [
        "home.HomePage", "home.Section", "home.Article", "questionnaires.SurveyIndexPage", 'home.FooterIndexPage',
    ]
    template = "survey/survey.html"
    multi_step = models.BooleanField(
        default=False,
        verbose_name=_("Multi-step"),
        help_text=_("Whether to display the survey questions to the user one at"
        " a time, instead of all at once."),
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
                FieldPanel("description"),
            ],
            heading=_(
                "Description at survey page",
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("thank_you_text"),
            ],
            heading="Description at thank you page",
        ),
        FieldPanel('index_page_description'),
        FieldPanel('index_page_description_line_2'),
        MultiFieldPanel(
            [
                FieldPanel("terms_and_conditions"),
            ],
            heading="Terms and conditions",
        ),
        SvgChooserPanel('icon'),
        FieldPanel('image_icon'),
        InlinePanel("survey_form_fields", label="Form fields"),
    ]

    translatable_fields = [
        TranslatableField('title'),
        TranslatableField('description'),
        TranslatableField('submit_button_text'),
        TranslatableField('survey_form_fields'),
        TranslatableField('thank_you_text')
    ]
    promote_panels = Page.promote_panels + [
        MultiFieldPanel([FieldPanel("notification_tags"), ], heading='Metadata'),
    ]
    @cached_property
    def has_page_breaks(self):
        return any(
            field.page_break
            for field in self.get_form_fields()
        )

    def get_form_class_for_step(self, step):
        return self.form_builder(step.object_list).get_form_class()

    def get_form_fields(self):
        return self.survey_form_fields.all()

    def get_submission_class(self):
        return UserSubmission
    
    def is_registration_survey(self):
        from home.models import SiteSettings
        site_settings = SiteSettings.get_for_default_site()
        if site_settings.registration_survey and site_settings.registration_survey.localized.pk == self.pk:
            return True
        else:
            return False

    def process_form_submission(self, form):
        from home.models import SiteSettings

        super().process_form_submission(form)

        site_settings = SiteSettings.get_for_default_site()
        if site_settings.registration_survey and site_settings.registration_survey.localized.pk == self.pk:
            user = form.user
            user.has_filled_registration_survey = True
            user.save(update_fields=['has_filled_registration_survey'])

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({'back_url': request.GET.get('back_url')})
        context.update({'form_length': request.GET.get('form_length')})
        return context

    def has_required_fields(self):
        return self.survey_form_fields.filter(required=True).exists()

    class Meta:
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")


class UserSubmission(AbstractFormSubmission):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True
    )
    session_key = models.CharField(max_length=255, null=True, blank=True)

    def get_data(self):
        form_data = super().get_data()
        form_data.update(
            {
                "user": self.user if self.user else None,
                "page_url": self.page.full_url,
            }
        )
        return form_data


class PollFormField(AbstractFormField):
    page = ParentalKey("Poll", on_delete=models.CASCADE, related_name="poll_form_fields")
    CHOICES = (
        ('checkboxes', _('Checkboxes')),
        ('dropdown', _('Dropdown')),
        ('multiline', _('Multi-line text')),
        ('radio', _('Radio buttons')),
    )
    clean_name = models.TextField(
        verbose_name=_('name'),
        blank=True,
        default='',
        help_text=_('Safe name of the form field, the label converted to ascii_snake_case. '
                    'This will appear in the HTML but will not be visible to the user')
    )
    label = models.TextField(
        verbose_name=_('label'),
        help_text=_('The label of the form field')
    )
    field_type = models.CharField(
        verbose_name=_('field type'),
        max_length=16,
        choices=CHOICES
    )
    choices = models.TextField(
        verbose_name=_('choices'),
        null=True,
        blank=True,
        help_text=_('For checkboxes, dropdown and radio: Pipe (|) separated list of choices.')
    )
    default_value = models.TextField(
        verbose_name=_('default value'),
        blank=True,
        help_text=_('Default value. Pipe (|) separated values supported for checkboxes.')
    )
    admin_label = models.CharField(
        verbose_name=_('admin_label'),
        max_length=256,
        help_text=_('Column header used during CSV export of poll responses.'),
        null=True
    )

    panels = [
        FieldPanel('label'),
        FieldPanel('clean_name', classname='disabled-clean-name'),
        FieldPanel('help_text'),
        FieldPanel('required'),
        FieldPanel('field_type', classname="formbuilder-type"),
        FieldPanel('choices', classname="formbuilder-choices"),
        FieldPanel('default_value', classname="formbuilder-default"),
        FieldPanel('admin_label'),
    ]


class Poll(QuestionnairePage, AbstractForm):
    form_builder = CustomFormBuilder
    template = "poll/poll.html"
    parent_page_types = [
        "home.HomePage", "home.Section", "home.Article", "questionnaires.PollIndexPage", 'home.FooterIndexPage',
    ]

    show_results = models.BooleanField(
        default=True, help_text=_("This option allows the users to see the results.")
    )
    result_as_percentage = models.BooleanField(
        default=True,
        help_text=_(
            "If not checked, the results will be shown as a total instead of a percentage."
        ),
    )
    randomise_options = models.BooleanField(
        default=False,
        help_text=_(
            "Randomising the options allows the options to be shown in a different "
            "order each time the page is displayed."
        ),
    )
    show_results_with_no_votes = models.BooleanField(
        default=True,
        help_text=_("Display options with 0 votes in results.")
    )

    content_panels = Page.content_panels + [
        FormSubmissionsPanel(),
        MultiFieldPanel(
            [
                FieldPanel("allow_anonymous_submissions"),
                FieldPanel("show_results"),
                FieldPanel("result_as_percentage"),
                FieldPanel("allow_multiple_submissions"),
                FieldPanel("randomise_options"),
                FieldPanel("show_results_with_no_votes"),
                FieldPanel("submit_button_text"),
            ],
            heading=_(
                "General settings for poll",
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("description"),
            ],
            heading=_(
                "Description at poll page",
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("thank_you_text"),
            ],
            heading="Description at thank you page",
        ),
        FieldPanel('index_page_description'),
        FieldPanel('index_page_description_line_2'),
        MultiFieldPanel(
            [
                FieldPanel("terms_and_conditions"),
            ],
            heading="Terms and conditions",
        ),
        SvgChooserPanel('icon'),
        FieldPanel('image_icon'),
        InlinePanel("poll_form_fields", label="Poll Form fields", min_num=1, max_num=1),
    ]

    class Meta:
        verbose_name = _("poll")
        verbose_name_plural = _("polls")

    def get_form_fields(self):
        return self.poll_form_fields.all()

    def get_submission_class(self):
        return UserSubmission

    def get_results(self, data=None):
        results = dict()
        results_list = []
        field = self.get_form_fields().first()
        name, choices = field.clean_name, field.choices
        submissions = self.get_submission_class().objects.filter(page=self)
        submissions = [submission for submission in submissions if submission.get_data().get(name) != '']

        # Default result counts to zero so choices with no votes are included
        if self.show_results_with_no_votes:
            results[name] = {
                choice: 0 for choice in choices.split('|') if len(choice) > 0
            }

        for submission in submissions:
            data = submission.get_data()
            answer = data.get(name)
            question_stats = results.get(name, {})
            if type(answer) != list:
                answer = [answer]

            for choice in answer:
                question_stats[choice] = question_stats.get(choice, 0) + 1

            results[name] = question_stats

        if submissions and self.result_as_percentage:
            total_submissions = len(submissions)
            for key in results:
                for k, v in results[key].items():
                    results[key][k] = round(v / total_submissions, 4) * 100

        for question, answers in results.items():
            for answer, count in answers.items():
                is_selected = data and (answer in data.get(question))
                results_list.append((answer, round(count), is_selected))

        return results_list

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        results = self.get_results(dict(request.POST))

        context.update({
            'results': results,
            'result_as_percentage': self.result_as_percentage,
            'back_url': request.GET.get('back_url'),
        })
        return context

    def get_submit_button_text(self, fields_step=None):
        return self.submit_button_text


class QuizFormField(AbstractFormField, ClusterableModel):
    page = ParentalKey("Quiz", on_delete=models.CASCADE, related_name="quiz_form_fields")
    clean_name = models.TextField(
        verbose_name=_('name'),
        blank=True,
        default='',
        help_text=_('Safe name of the form field, the label converted to ascii_snake_case. '
                    'This will appear in the HTML but will not be visible to the user')
    )
    label = models.TextField(
        verbose_name=_('label'),
        help_text=_('The label of the form field')
    )
    field_type = models.CharField(
        verbose_name=_('field type'),
        max_length=16,
        choices=FORM_FIELD_CHOICES
    )
    choices = models.TextField(
        verbose_name=_('choices'),
        blank=True,
        help_text=_('For checkboxes, dropdown and radio: Pipe (|) separated list of choices.')
    )
    admin_label = models.CharField(
        verbose_name=_('admin_label'),
        max_length=256,
        help_text=_('Column header used during CSV export of survey '
                    'responses.'),
    )
    default_value = models.TextField(
        verbose_name=_('default value'),
        blank=True,
        help_text=_('Default value. Pipe (|) separated values supported for checkboxes.')
    )
    page_break = models.BooleanField(
        default=False,
        help_text=_(
            'Inserts a page break which puts the next question onto a new page'
        )
    )
    correct_answer = models.TextField(
        verbose_name=_('correct_answer'),
        help_text=_('The correct answer/choice(s). '
                    'If multiple choices are correct, separate choices with a pipe (|) symbol. '
                    'For checkbox: Either "true" or "false".'))
    feedback = models.TextField(
        verbose_name=_('Feedback'),
        null=True,
        blank=True,
        help_text=_('Feedback message for user answer.')
    )

    panels = [
        FieldPanel('label'),
        FieldPanel('clean_name', classname='disabled-clean-name'),
        FieldPanel('help_text'),
        FieldPanel('required'),
        FieldPanel('field_type', classname="formbuilder-type"),
        FieldPanel('choices', classname="formbuilder-choices"),
        FieldPanel('default_value', classname="formbuilder-default"),
        FieldPanel('correct_answer'),
        FieldPanel('feedback'),
        FieldPanel('admin_label'),
        FieldPanel('page_break'),
        InlinePanel('quiz_choices', label='Choices with feedback'),
    ]

    @property
    def has_skipping(self):
        return None

    def choice_index(self, choice):
        if choice:
            if self.field_type == 'checkbox':
                # clean checkboxes have True/False
                try:
                    return ['true', 'false'].index(choice)
                except ValueError:
                    return [True, False].index(choice)
            try:
                return self.choices.split('|').index(choice)
            except ValueError:
                pass

        return None

    def next_action(self, choice):
        choice_index = self.choice_index(choice)
        if choice_index is None:
            return SkipState.NEXT
        return self.skip_logic[choice_index].value['skip_logic']

    def is_next_action(self, choice, *actions):
        if self.has_skipping:
            return self.next_action(choice) in actions
        return False

    def next_page(self, choice):
        logic = self.skip_logic[self.choice_index(choice)]
        return logic.value[self.next_action(choice)]


class Quiz(QuestionnairePage, AbstractForm):
    base_form_class = QuizForm
    form_builder = CustomFormBuilder

    parent_page_types = [
        "home.HomePage", "home.Section", "home.Article", "questionnaires.QuizIndexPage", 'home.FooterIndexPage',
    ]
    template = "quizzes/quiz.html"

    multi_step = models.BooleanField(
        default=False,
        verbose_name=_("Multi-step"),
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
                "General settings for quiz",
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("description"),
            ],
            heading=_(
                "Description at quiz page",
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("thank_you_text"),
            ],
            heading="Description at thank you page",
        ),
        FieldPanel('index_page_description'),
        FieldPanel('index_page_description_line_2'),
        MultiFieldPanel(
            [
                FieldPanel("terms_and_conditions"),
            ],
            heading="Terms and conditions",
        ),
        SvgChooserPanel('icon'),
        FieldPanel('image_icon'),
        InlinePanel("quiz_form_fields", label="Form fields"),
    ]

    @cached_property
    def has_page_breaks(self):
        return any(
            field.page_break
            for field in self.get_form_fields()
        )

    def get_form_class_for_step(self, step):
        return self.form_builder(step.object_list).get_form_class()

    def get_form_fields(self):
        return self.quiz_form_fields.all()

    def get_submission_class(self):
        return UserSubmission

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.update({'back_url': request.GET.get('back_url')})
        context.update({'form_length': request.GET.get('form_length')})
        from iogt_users.models import QuizAttempt
        form_helper = FormHelper(pk=self.pk, request=request)
        if self.multi_step:
            form_data = form_helper.get_full_form_data()
        else:
            if request.GET.get('view') == 'answers' and request.user.is_authenticated:
                user = request.user
                last_attempt = QuizAttempt.objects.filter(user=user, quiz=self).order_by('-completed_at').first()
                if last_attempt:
                    form_data = last_attempt.submitted_answers or {}
            else:
                form_data = request.POST
        
        if form_data:
            form = self.get_form(
                data=form_data,
                page=self, user=request.user
            )
            fields_info = {}
            total = 0
            total_correct = 0
            form_data = dict(form.data)
            for field in self.get_form_fields():
                correct_answer = field.correct_answer.split('|')
                
                if field.field_type == 'checkbox':
                    answer = 'true' if form_data.get(field.clean_name) else 'false'
                else:
                    answer = form_data.get(field.clean_name)

                if type(answer) != list:
                    answer = [str(answer)]

                if field.field_type in ['radio', 'dropdown']:
                    is_correct = set(answer).issubset(set(correct_answer))
                else:
                    is_correct = set(answer) == set(correct_answer)

                if is_correct:
                    total_correct += 1
                total += 1
                selected_feedbacks = []
                for selected_value in answer:
                    choice_feedback = field.quiz_choices.filter(choice_text=selected_value).first()
                    if choice_feedback  and choice_feedback.feedback:
                        selected_feedbacks.append(choice_feedback.feedback)
                if selected_feedbacks:
                    feedback_text = selected_feedbacks
                elif field.feedback:
                    feedback_text = [field.feedback]
                else:
                    feedback_text = []
                fields_info[field.clean_name] = {
                    'feedback': feedback_text,
                    'correct_answer': field.correct_answer,
                    'correct_answer_list': correct_answer,
                    'is_correct': is_correct,
                    'selected_answer': answer
                }
            context['form'] = form
            context['fields_info'] = fields_info
            context['result'] = {
                'total': total,
                'total_correct': total_correct,
            }
            user = request.user
            if user.is_authenticated:
                score_percentage = (total_correct / total) * 100 if total else 0
                attempt_number = QuizAttempt.objects.filter(user=user, quiz=self).count() + 1
                if request.method == 'POST':
                    QuizAttempt.objects.create(
                        user=user,
                        quiz=self,
                        score=score_percentage,
                        attempt_number=attempt_number,
                        completed_at=timezone.now(),
                        submitted_answers=form_data
                    )
                avg_score = QuizAttempt.objects.filter(user=user, quiz=self).aggregate(Avg('score'))['score__avg'] or 0
                context['average_score'] = avg_score
                context['attempt_number'] = attempt_number
            if self.multi_step:
                form_helper.remove_session_data()
        return context

    class Meta:
        verbose_name = _("quiz")
        verbose_name_plural = _("quizzes")

class QuizChoice(Orderable):
    question = ParentalKey(
        'QuizFormField',
        related_name='quiz_choices',
        on_delete=models.CASCADE
    )
    choice_text = models.CharField(
        max_length=255,
        verbose_name='Choice Text',
        blank=True,
        null=True,
        help_text='The option text that users will see',
    )
    feedback = models.TextField(
        verbose_name='Feedback',
        blank=True,
        null=True,
        help_text='Feedback specific to this choice (optional).',
    )
    panels = [
        FieldPanel('choice_text'),
        FieldPanel('feedback'),
    ]
    def __str__(self):
        return f"{self.choice_text} "


class PollIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['questionnaires.Poll']


class SurveyIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['questionnaires.Survey']


class QuizIndexPage(Page):
    parent_page_types = ['home.HomePage']
    subpage_types = ['questionnaires.Quiz']


class RegistrationSurvey(models.Model):
    """
    Model to store user registration survey data for Superset visualization.
    """

    age_category = models.CharField(
        max_length=50,
        choices=[
            ("Child", "Child"),
            ("Youth", "Youth"),
            ("Adult", "Adult"),
            ("Senior", "Senior"),
        ],
    )
    gender = models.CharField(
        max_length=20,
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
            ("Prefer not to say", "Prefer not to say"),
        ],
    )
    count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "registration_survey"

    def __str__(self):
        return f"{self.age_category} - {self.gender} ({self.count})"
