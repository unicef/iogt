from django.urls import path
from . import views

app_name = 'cranky_uncle'

urlpatterns = [
    # path('cranky-home/', views.CrankyUncleHomeView.as_view(), name='cranky-home'),
    # path('cranky-home/', views.cranky_uncle_home, name='cranky-home'),
    # path('cranky-home/', views.CrankyUncleHomeView.as_view(), name='cranky-home'),
    path('cranky-quiz/<slug:slug>/', views.CrankyUncleQuizView.as_view(), name='cranky-quiz'),
    path('rapidpro-message-hook/', views.RapidProMessageHook.as_view(), name='rapidpro-message-hook')
]