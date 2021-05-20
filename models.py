from django.db import models
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel, 
    MultiFieldPanel
)
from wagtail.core.fields import RichTextField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField


class FormField(AbstractFormField):
    page = ParentalKey('PollPage', default=1, on_delete=models.CASCADE, related_name='form_fields'
        )


class PollPage(AbstractEmailForm):

    template = "poll/poll_page.html"
    
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

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

