from django.conf import settings
from rest_framework import permissions


class IsRapidProGroupUser(permissions.BasePermission):
    message = "User is not allowed to access the webhook"

    def has_permission(self, request, view):
        return request.user.groups.filter(
            name=settings.RAPIDPRO_BOT_GROUP_NAME
        ).exists()
