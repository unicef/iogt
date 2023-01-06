from django.core.management.base import BaseCommand

from questionnaires.models import SurveyFormField


class Command(BaseCommand):

    def handle(self, *args, **options):
        survey_form_fields = SurveyFormField.objects.all()
        for survey_form_field in survey_form_fields:
            if survey_form_field.skip_logic:
                skip_logics = survey_form_field.skip_logic.raw_data
                for skip_logic in skip_logics:
                    skip_logic.get('value', {}).pop('survey', None)

        SurveyFormField.objects.bulk_update(survey_form_fields, fields=['skip_logic'], batch_size=1000)

        self.stdout.write(self.style.SUCCESS('Fixed surveys skip logic.'))
