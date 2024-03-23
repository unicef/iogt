from django.urls import path

from .views import RapidProWebhook

urlpatterns = [
    path('rapidpro-webhook/', RapidProWebhook.as_view(), name='rapidpro_message_webhook')
]
