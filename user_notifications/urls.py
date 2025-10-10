# user_notifications/urls.py
from django.urls import path
from . import views

app_name = 'user_notifications'

urlpatterns = [
    path('latest_notifications/', views.latest_notifications, name='latest_notifications'),
    path('all/', views.all_notifications, name='all'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('mark-selected-read/', views.mark_selected_read, name='mark_selected_read'),
    path('toggle-read/<int:pk>/', views.toggle_read, name='toggle_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('mark-clicked/<int:notification_id>/', views.mark_notification_clicked, name='mark_notification_clicked')

]
