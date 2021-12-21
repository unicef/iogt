from django.urls import path
from iogt_users.views import UserDetailEditView, UserDetailView

urlpatterns = [
    path('profile/', UserDetailView.as_view(), name='user_profile'),
    path('profile/edit', UserDetailEditView.as_view(), name='user_profile_edit')
]