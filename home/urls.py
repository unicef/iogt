from django.urls import path
from home.views import  TestView

urlpatterns = [
    path("", TestView.as_view(), name="test"),
]