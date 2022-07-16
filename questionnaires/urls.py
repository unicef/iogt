from django.urls import path

from questionnaires.views import QuestionnairesListAPIView

urlpatterns = [
    path('list/', QuestionnairesListAPIView.as_view(), name='questionnaires_list'),
]
