from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from home.models import HomePage
from questionnaires.models import PollIndexPage, SurveyIndexPage, QuizIndexPage


class Command(BaseCommand):

    def handle(self, *args, **options):
        homepage = HomePage.objects.get(slug='home')
        poll_index_page = PollIndexPage(title='Polls')
        survey_index_page = SurveyIndexPage(title='Surveys')
        quiz_index_page = QuizIndexPage(title='Quizzes')

        homepage.add_child(instance=poll_index_page)
        homepage.add_child(instance=survey_index_page)
        homepage.add_child(instance=quiz_index_page)
        self.stdout.write(self.style.SUCCESS('Index pages added.'))
