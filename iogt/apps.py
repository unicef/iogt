# myproject/apps.py
from wagtail.users.apps import WagtailUsersAppConfig


class CustomUsersAppConfig(WagtailUsersAppConfig):
    user_viewset = "iogt_users.viewsets.UserViewSet"