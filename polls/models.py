import json
from django import forms
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
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


class CustomFormBuilder(FormBuilder):
    def create_positivenumber_field(self, field, options):
        return forms.NumberInput(**options)


class PollPage(AbstractEmailForm):

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    require_login = models.BooleanField(default=True)
    multiple_responses = models.BooleanField(default=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('require_login'),
        FieldPanel('multiple_responses'),
        FieldPanel('intro', classname="full"),
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

    def serve(self, request, *args, **kwargs):
        try:
            if self.get_submission_class().objects.filter(page=self, user__pk=request.user.pk).exists():
                try:
                    PollPage.objects.get(Q(page_ptr_id=self.id), Q(Q(require_login=False), Q(multiple_responses=False)))
                    return render(
                        request,
                        self.template,
                        self.get_context(request)
                    )
                except ObjectDoesNotExist:
                    return super().serve(request, *args, **kwargs)
            else:
                return super().serve(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return super().serve(request, *args, **kwargs)

    def get_submission_class(self):
        return CustomPollSubmission

    def process_form_submission(self, form):
        self.get_submission_class().objects.create(
            form_data=json.dumps(form.cleaned_data, cls=DjangoJSONEncoder),
            page=self, user=form.user
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_data(self):
        form_data = super().get_data()
        form_data.update({
            'Admin Name': self.user.username,
        })

        return form_data
