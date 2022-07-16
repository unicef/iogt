from django_filters import rest_framework as filters
from wagtail.core.models import Page


class QuestionnaireFilter(filters.FilterSet):
    published_at_start = filters.DateFilter(field_name='last_published_at__date', lookup_expr='gte')
    published_at_end = filters.DateFilter(field_name="last_published_at__date", lookup_expr='lte')
    type = filters.ChoiceFilter(field_name='content_type__model', lookup_expr='exact',
                                choices=(('poll', 'Poll'), ('survey', 'Survey'), ('quiz', 'Quiz')))

    class Meta:
        model = Page
        fields = '__all__'
