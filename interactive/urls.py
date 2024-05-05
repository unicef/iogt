from django.urls import path, include

from interactive.views import InteractiveView

app_name = 'interactive'

urlpatterns = [
    path('api/', include('interactive.api.urls')),
    path('<slug:slug>/', InteractiveView.as_view(), name='interactive_game'),
]