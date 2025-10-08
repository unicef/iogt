from django.urls import path
from iogt_users.views import UserDetailEditView, UserDetailView, InviteAdminUserView, UserNotificationView
from user_notifications.views import save_notification_preference

urlpatterns = [
    path('invite-admin-user/', InviteAdminUserView.as_view(), name='invite_admin_user'),
    path('profile/', UserDetailView.as_view(), name='user_profile'),
    path('profile/edit', UserDetailEditView.as_view(), name='user_profile_edit'),
    path('profile/edit', UserDetailEditView.as_view(), name='user_profile_edit'),
    path('notifications/settings/', UserNotificationView.as_view(), name='notification_settings'),
    path("notifications/save-preference/", save_notification_preference, name="save_notification_preference"),
]