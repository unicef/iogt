from django_filters import rest_framework as filters
from wagtail.core.models import Page

from iogt.filters import ListIdFilter
from questionnaires.models import UserSubmission


class QuestionnaireFilter(filters.FilterSet):
    published_at_start = filters.DateFilter(field_name='last_published_at__date', lookup_expr='gte')
    published_at_end = filters.DateFilter(field_name="last_published_at__date", lookup_expr='lte')
    type = filters.ChoiceFilter(field_name='content_type__model', lookup_expr='exact',
                                choices=(('poll', 'Poll'), ('survey', 'Survey'), ('quiz', 'Quiz')))

    class Meta:
        model = Page
        fields = ['published_at_start', 'published_at_end', 'type']


class SubmissionFilter(filters.FilterSet):
    submit_at_start = filters.DateFilter(field_name='submit_time__date', lookup_expr='gte')
    submit_at_end = filters.DateFilter(field_name="submit_time__date", lookup_expr='lte')
    user_ids = ListIdFilter(field_name='user_id')

    class Meta:
        model = UserSubmission
        fields = ['submit_at_start', 'submit_at_end', 'user_ids']
