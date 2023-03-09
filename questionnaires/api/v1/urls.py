from django.urls import path

from questionnaires.api.v1.views import (
    QuestionnairesListAPIView,
    QuestionnaireDetailAPIView,
    QuestionnaireSubmissionsAPIView,
)

urlpatterns = [
    path('', QuestionnairesListAPIView.as_view(), name='questionnaires_list'),
    path('<int:pk>/', QuestionnaireDetailAPIView.as_view(), name='questionnaire_detail'),
    path('<int:pk>/submissions/', QuestionnaireSubmissionsAPIView.as_view(), name='questionnaire_submissions'),
]
