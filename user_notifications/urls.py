# user_notifications/urls.py
from django.urls import path
from . import views

app_name = 'user_notifications'

urlpatterns = [
    path('dropdown/', views.latest_notifications, name='dropdown'),
    path('all/', views.all_notifications, name='all'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('toggle-read/<int:pk>/', views.toggle_read, name='toggle_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
]
