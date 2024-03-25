from django_filters import rest_framework as filters
from wagtail.models import Page

from questionnaires.models import UserSubmission


class ListIdFilter(filters.Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_expr = 'in'

    def filter(self, queryset, value):
        list_values = value.split(',') if value else []
        return super().filter(queryset, list_values)


class QuestionnaireFilter(filters.FilterSet):
    last_published_at_start = filters.DateFilter(field_name='last_published_at__date', lookup_expr='gte')
    last_published_at_end = filters.DateFilter(field_name="last_published_at__date", lookup_expr='lte')
    type = filters.ChoiceFilter(field_name='content_type__model', lookup_expr='exact',
                                choices=(('poll', 'Poll'), ('survey', 'Survey'), ('quiz', 'Quiz')))

    class Meta:
        model = Page
        fields = ['last_published_at_start', 'last_published_at_end', 'type']


class UserSubmissionFilter(filters.FilterSet):
    submit_time_start = filters.DateFilter(field_name='submit_time__date', lookup_expr='gte')
    submit_time_end = filters.DateFilter(field_name="submit_time__date", lookup_expr='lte')
    user_ids = ListIdFilter(field_name='user_id')

    class Meta:
        model = UserSubmission
        fields = ['submit_time_start', 'submit_time_end', 'user_ids']
