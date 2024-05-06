from django.urls import path

from .views import RapidProWebhook

app_name = 'interactive_api'

urlpatterns = [
    path('rapidpro-webhook/', RapidProWebhook.as_view(), name='rapidpro_message_webhook')
]
