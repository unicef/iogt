from django.urls import path, include

from .api.urls import urlpatterns as api_urls
from . import views

app_name = "messaging"

urlpatterns = [
    path('api/', include(api_urls)),
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('message/<int:thread_id>', views.ThreadDetailView.as_view(), name='thread'),
    path('message/create', views.MessageCreateView.as_view(), name='message_create'),
    path('thread/<int:pk>/delete/', views.ThreadDeleteView.as_view(), name="thread_delete"),
]

