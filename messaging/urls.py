from django.urls import path, include

from . import views

app_name = "messaging"

urlpatterns = [
    path('api/', include('messaging.api.urls')),
    path('inbox/', views.InboxView.as_view(), name='inbox'),
    path('message/<int:thread_id>', views.ThreadDetailView.as_view(), name='thread'),
    path('message/create', views.MessageCreateView.as_view(), name='message_create'),
    path('thread/<int:pk>/delete/', views.ThreadDeleteView.as_view(), name="thread_delete"),
]

