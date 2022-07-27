from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from wagtail.contrib.forms.utils import get_forms_for_user

from questionnaires.filters import QuestionnaireFilter, UserSubmissionFilter
from questionnaires.models import Survey, Poll, Quiz, UserSubmission
from iogt.paginators import IoGTPagination
from questionnaires.serializers import (
    QuestionnairePageSerializer,
    SurveyPageDetailSerializer,
    PollPageDetailSerializer,
    QuizPageDetailSerializer,
    UserSubmissionSerializer,
    QuestionnairePageDetailSerializer,
)


@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('last_published_at_start', openapi.IN_QUERY, format="YYYY-MM-DD", type=openapi.TYPE_STRING),
        openapi.Parameter('last_published_at_end', openapi.IN_QUERY, format="YYYY-MM-DD", type=openapi.TYPE_STRING),
        openapi.Parameter('type', openapi.IN_QUERY, enum=['poll', 'survey', 'quiz'], type=openapi.TYPE_STRING),
    ],
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Questionnaires List API",
            schema=QuestionnairePageSerializer,
        )
    }
))
class QuestionnairesListAPIView(ListAPIView):
    serializer_class = QuestionnairePageSerializer
    filterset_class = QuestionnaireFilter
    pagination_class = IoGTPagination

    def get_queryset(self):
        return get_forms_for_user(self.request.user).order_by('-last_published_at')


@method_decorator(name='get', decorator=swagger_auto_schema(
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Questionnaire Page Detail API",
            schema=QuestionnairePageDetailSerializer,
        )
    }
))
class QuestionnaireDetailAPIView(RetrieveAPIView):
    def get_queryset(self):
        return get_forms_for_user(self.request.user).specific().order_by('-last_published_at')

    def get_serializer_class(self):
        page = self.get_object()
        if isinstance(page, Poll):
            return PollPageDetailSerializer
        elif isinstance(page, Survey):
            return SurveyPageDetailSerializer
        elif isinstance(page, Quiz):
            return QuizPageDetailSerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('submit_time_start', openapi.IN_QUERY, format="YYYY-MM-DD", type=openapi.TYPE_STRING),
        openapi.Parameter('submit_time_end', openapi.IN_QUERY, format="YYYY-MM-DD", type=openapi.TYPE_STRING),
        openapi.Parameter('user_ids', openapi.IN_QUERY, format='Comma (,) separated with no spaces', type=openapi.TYPE_STRING),
    ],
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Questionnaire Submissions List API",
            schema=UserSubmissionSerializer,
        )
    }
))
class QuestionnaireSubmissionsAPIView(ListAPIView):
    serializer_class = UserSubmissionSerializer
    filterset_class = UserSubmissionFilter
    pagination_class = IoGTPagination

    def get_queryset(self):
        return UserSubmission.objects.filter(
            page_id=self.kwargs.get(self.lookup_field),
            page__in=get_forms_for_user(self.request.user)
        ).select_related(
            'user', 'page'
        ).order_by('-submit_time')
