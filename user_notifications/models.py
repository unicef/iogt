from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from django.utils.timezone import now
from wagtail.fields import RichTextField
from iogt.settings.base import AUTH_USER_MODEL

@register_snippet
class UserNotificationTemplate(models.Model):
    title = models.CharField(max_length=255)
    message = RichTextField(features=["bold", "italic", "link", "ul", "ol"])
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(default=now)

    panels = [
        FieldPanel('title'),
        FieldPanel('message'),
        FieldPanel('active'),
    ]

    def __str__(self):
        return f"{self.title} ({'active' if self.active else 'inactive'})"

    class Meta:
        verbose_name = "User Notification Template"
        verbose_name_plural = "User Notification Templates"


class NotificationPreference(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    receive_notifications = models.BooleanField(null=True, blank=True)  # NULL = not chosen yet

    def __str__(self):
        return f"{self.user.username} preferences"
