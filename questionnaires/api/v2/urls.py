from django.urls import path

from questionnaires.api.v2.views import (
    QuestionnaireSubmissionsAPIView,
)

urlpatterns = [
    path('<int:pk>/submissions/', QuestionnaireSubmissionsAPIView.as_view(), name='v2_questionnaire_submissions'),
]
