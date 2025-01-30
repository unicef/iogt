from django.urls import path
from iogt_users.views import UserDetailEditView, UserDetailView, InviteAdminUserView

urlpatterns = [
    path('invite-admin-user/', InviteAdminUserView.as_view(), name='invite_admin_user'),
    path('profile/', UserDetailView.as_view(), name='user_profile'),
    path('profile/edit', UserDetailEditView.as_view(), name='user_profile_edit'),
]