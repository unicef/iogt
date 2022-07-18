from rest_framework.generics import ListAPIView, RetrieveAPIView
from wagtail.contrib.forms.views import SubmissionsListView, FormPagesListView as WagtailFormPagesListView
from wagtail.core.models import Page

from questionnaires.filters import QuestionnaireFilter, UserSubmissionFilter
from questionnaires.models import QuestionnairePage, Survey, Poll, Quiz, UserSubmission
from iogt.paginators import IoGTPagination
from questionnaires.serializers import (
    QuestionnairePageSerializer,
    SurveyPageDetailSerializer,
    PollPageDetailSerializer,
    QuizPageDetailSerializer,
    UserSubmissionSerializer
)


class FormPagesListView(WagtailFormPagesListView):
    def get_queryset(self):
        from home.models import SiteSettings

        queryset = super().get_queryset()
        registration_survey = SiteSettings.get_for_default_site().registration_survey
        if registration_survey:
            ids = registration_survey.get_translations(inclusive=True).values_list('id', flat=True)
            if ids:
                queryset = queryset.exclude(id__in=ids)
        return queryset


class CustomSubmissionsListView(SubmissionsListView):
    def get_filename(self):
        return self.form_page.get_export_filename()

    def get_queryset(self):
        return super().get_queryset().select_related('page', 'user')


class QuestionnairesListAPIView(ListAPIView):
    queryset = Page.objects.type(QuestionnairePage).order_by('-last_published_at')
    serializer_class = QuestionnairePageSerializer
    filterset_class = QuestionnaireFilter
    pagination_class = IoGTPagination


class QuestionnaireDetailAPIView(RetrieveAPIView):
    queryset = Page.objects.type(QuestionnairePage).specific()

    def get_serializer_class(self):
        page = self.get_object()
        if isinstance(page, Poll):
            return PollPageDetailSerializer
        elif isinstance(page, Survey):
            return SurveyPageDetailSerializer
        elif isinstance(page, Quiz):
            return QuizPageDetailSerializer


class QuestionnaireSubmissionsAPIView(ListAPIView):
    serializer_class = UserSubmissionSerializer
    filterset_class = UserSubmissionFilter
    pagination_class = IoGTPagination

    def get_queryset(self):
        return UserSubmission.objects.filter(
            page=self.kwargs.get(self.lookup_field)
        ).select_related(
            'user', 'page'
        ).order_by('-submit_time')
