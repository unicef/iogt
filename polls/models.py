import json
from django.db import models
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField, AbstractFormSubmission
from modelcluster.fields import ParentalKey

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render


class FormField(AbstractFormField):
    page = ParentalKey('PollPage', on_delete=models.CASCADE, related_name='form_fields')


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

    def serve(self, request, *args, **kwargs):
        if self.get_submission_class().objects.filter(page=self, user__pk=request.user.pk).exists():
            return render(
                request,
                self.template,
                self.get_context(request)
            )

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

    class Meta:
        unique_together = ('page', 'user')
