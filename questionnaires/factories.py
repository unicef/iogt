import factory
from wagtail_factories import PageFactory

from questionnaires.models import Survey, Poll, Quiz


class PollFactory(PageFactory):
    title = factory.Sequence(lambda n: f'poll{n}')

    class Meta:
        model = Poll


class SurveyFactory(PageFactory):
    title = factory.Sequence(lambda n: f'survey{n}')

    class Meta:
        model = Survey


class QuizFactory(PageFactory):
    title = factory.Sequence(lambda n: f'quiz{n}')

    class Meta:
        model = Quiz
