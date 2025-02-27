from django.urls import path
from home.views import AdminArticleFeedbackView, submit_feedback, load_more_reviews

urlpatterns = [
    path('article-feedback/<int:article_id>/', AdminArticleFeedbackView, name='admin_article_feedback'),
    path('submit-feedback/<int:article_id>/', submit_feedback, name='submit_feedback_article'),
    path('load-more-reviews/<int:article_id>/', load_more_reviews, name='load_more_reviews'),
]
