from django.urls import path

from questionnaires.views import QuestionnairesListAPIView, QuestionnaireDetailAPIView

urlpatterns = [
    path('list/', QuestionnairesListAPIView.as_view(), name='questionnaires_list'),
    path('<int:pk>/', QuestionnaireDetailAPIView.as_view(), name='questionnaire_detail'),
]
