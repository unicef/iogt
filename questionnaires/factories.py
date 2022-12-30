import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory, ImageFactory

from questionnaires.models import Survey, Poll, Quiz, PollFormField, SurveyFormField, QuizFormField, UserSubmission


class PollFormFieldFactory(DjangoModelFactory):
    label = factory.Sequence(lambda n: f'question{n}')
    admin_label = factory.Sequence(lambda n: f'question{n}')
    help_text = factory.Sequence(lambda n: f'help text{n}')

    class Meta:
        model = PollFormField


class PollFactory(PageFactory):
    title = factory.Sequence(lambda n: f'poll{n}')
    lead_image = factory.SubFactory(ImageFactory)
    last_published_at = timezone.now()
    index_page_description = factory.Sequence(lambda n: f'index page description{n}')
    index_page_description_line_2 = factory.Sequence(lambda n: f'index page description line 2{n}')

    class Meta:
        model = Poll


class SurveyFormFieldFactory(DjangoModelFactory):
    label = factory.Sequence(lambda n: f'question{n}')
    admin_label = factory.Sequence(lambda n: f'question{n}')
    help_text = factory.Sequence(lambda n: f'help text{n}')

    class Meta:
        model = SurveyFormField


class SurveyFactory(PageFactory):
    title = factory.Sequence(lambda n: f'survey{n}')
    lead_image = factory.SubFactory(ImageFactory)
    last_published_at = timezone.now()
    index_page_description = factory.Sequence(lambda n: f'index page description{n}')
    index_page_description_line_2 = factory.Sequence(lambda n: f'index page description line 2{n}')

    class Meta:
        model = Survey


class QuizFormFieldFactory(DjangoModelFactory):
    label = factory.Sequence(lambda n: f'question{n}')
    admin_label = factory.Sequence(lambda n: f'question{n}')
    help_text = factory.Sequence(lambda n: f'help text{n}')
    feedback = factory.Sequence(lambda n: f'feedback{n}')

    class Meta:
        model = QuizFormField


class QuizFactory(PageFactory):
    title = factory.Sequence(lambda n: f'quiz{n}')
    lead_image = factory.SubFactory(ImageFactory)
    last_published_at = timezone.now()
    index_page_description = factory.Sequence(lambda n: f'index page description{n}')
    index_page_description_line_2 = factory.Sequence(lambda n: f'index page description line 2{n}')

    class Meta:
        model = Quiz


class UserSubmissionFactory(DjangoModelFactory):
    class Meta:
        model = UserSubmission
