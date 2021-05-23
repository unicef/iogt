import json
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from rest_framework.exceptions import PermissionDenied
from rest_framework import status

from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField, AbstractFormSubmission, \
    FORM_FIELD_CHOICES
from wagtail.contrib.forms.forms import FormBuilder
from modelcluster.fields import ParentalKey

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render


class FormField(AbstractFormField):
    CHOICES = FORM_FIELD_CHOICES + (('positivenumber', 'Positive number'),)

    page = ParentalKey('PollPage', on_delete=models.CASCADE, related_name='form_fields')

    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=CHOICES
    )


class CustomException(PermissionDenied):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = {
        "result": False,
        "errorCode": 0,
        "errorMsg": "Internal Server Error"
    }

    def __init__(self, code, message, status_code=None):
        self.detail = {
            "result": False,
            "errorCode": code,
            "errorMsg": message
        }
        if status_code is not None:
            self.status_code = status_code


class CustomFormBuilder(FormBuilder):
    def create_positivenumber_field(self, field, options):
        return forms.NumberInput(**options)


class PollPage(AbstractEmailForm):
    template = "polls/poll_page.html"
    landing_page_template = "polls/poll_page_landing.html"

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    require_login = models.BooleanField(default=True)
    multiple_responses = models.BooleanField(default=True)
    lead_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('require_login'),
        FieldPanel('multiple_responses'),
        FieldPanel('intro', classname="full"),
        FieldPanel('lead_image'),
        InlinePanel('form_fields', label="Poll fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    form_builder = CustomFormBuilder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages = None

    def serve(self, request, *args, **kwargs):
        try:
            if PollPage.objects.get(page_ptr_id=self.id).require_login:
                try:
                    if self.get_submission_class().objects.filter(page=self, user__pk=request.user.pk).exists():
                        try:
                            if PollPage.objects.get(page_ptr_id=self.id, multiple_responses=False):
                                return render(
                                    request,
                                    self.template,
                                    self.get_context(request)
                                )
                            else:
                                return super().serve(request, *args, **kwargs)
                        except ObjectDoesNotExist:
                            return super().serve(request, *args, **kwargs)
                    else:
                        return render(
                            request,
                            self.template,
                            self.get_context(request)
                        )
                except ObjectDoesNotExist:
                    return render(
                        request,
                        self.template,
                        self.get_context(request)
                    )
            else:
                try:
                    if PollPage.objects.get(page_ptr_id=self.id, multiple_responses=False):
                        return render(
                            request,
                            self.template,
                            self.get_context(request)
                        )
                    else:
                        return super().serve(request, *args, **kwargs)
                except ObjectDoesNotExist:
                    return super().serve(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise CustomException(code=11, message=self.error_messages['invalid_page'])

    def get_submission_class(self):
        return CustomPollSubmission

    def process_form_submission(self, form):
        if form.user.is_authenticated:
            self.get_submission_class().objects.create(
                form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
                page=self, user=form.user
            )
        else:
            self.get_submission_class().objects.create(
                form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder), page=self
            )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        results = dict()
        data_fields = [
            (field.clean_name, field.label)
            for field in self.get_form_fields()
        ]

        submissions = self.get_submission_class().objects.filter(page=self)
        for submission in submissions:
            data = submission.get_data()

            for name, label in data_fields:
                answer = data.get(name)
                if answer is None:
                    continue

                if type(answer) is list:
                    answer = u', '.join(answer)

                question_stats = results.get(label, {})
                question_stats[answer] = question_stats.get(answer, 0) + 1
                results[label] = question_stats

        context.update({
            'results': results,
        })
        return context


class CustomPollSubmission(AbstractFormSubmission):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
