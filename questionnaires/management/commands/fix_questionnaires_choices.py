from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from home.models import HomePage
from questionnaires.models import PollIndexPage, SurveyIndexPage, QuizIndexPage, PollFormField, SurveyFormField, \
    QuizFormField


class Command(BaseCommand):

    def handle(self, *args, **options):
        poll_form_fields = PollFormField.objects.all()
        poll_form_field_list = []
        for poll_form_field in poll_form_fields:
            poll_form_field.choices = '|'.join(poll_form_field.choices.split(','))
            poll_form_field_list.append(poll_form_field)

        PollFormField.objects.bulk_update(poll_form_field_list, ['choices'], batch_size=1000)

        survey_form_fields = SurveyFormField.objects.all()
        survey_form_field_list = []
        for survey_form_field in survey_form_fields:
            survey_form_field.choices = '|'.join(survey_form_field.choices.split(','))
            survey_form_field_list.append(survey_form_field)

        SurveyFormField.objects.bulk_update(survey_form_field_list, ['choices'], batch_size=1000)

        quiz_form_fields = QuizFormField.objects.all()
        quiz_form_field_list = []
        for quiz_form_field in quiz_form_fields:
            quiz_form_field.choices = '|'.join(quiz_form_field.choices.split(','))
            quiz_form_field.correct_answer = '|'.join(quiz_form_field.correct_answer.split(','))
            quiz_form_field_list.append(quiz_form_field)

        QuizFormField.objects.bulk_update(quiz_form_field_list, ['choices', 'correct_answer'], batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Fixed questionnaires choices.'))
