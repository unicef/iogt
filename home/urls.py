from django.urls import path
from home.views import AdminArticleFeedbackView, submit_feedback

urlpatterns = [
    path('article-feedback/<int:article_id>/', AdminArticleFeedbackView, name='admin_article_feedback'),
    path('submit-feedback/<int:article_id>/', submit_feedback, name='submit_feedback_article'),
]
