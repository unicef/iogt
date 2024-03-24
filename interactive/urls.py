from django.urls import path

from interactive.views import InteractiveView

app_name = 'interactive'

urlpatterns = [
    path('<slug:slug>/', InteractiveView.as_view(), name='interactive_game'),
]