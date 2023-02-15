from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from wagtail.contrib.forms.utils import get_forms_for_user

from questionnaires.filters import UserSubmissionFilter
from questionnaires.models import UserSubmission
from questionnaires.paginators import IoGTPagination
from questionnaires.api.v2.serializers import (
    UserSubmissionSerializer,
)


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
    permission_classes = (IsAuthenticated,)
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
