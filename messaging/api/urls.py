from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from messaging.api.views import RapidProWebhook

app_name = 'api'

urlpatterns = [
    path('rapidpro-webhook/', RapidProWebhook.as_view(), name='rapidpro_webhook'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]