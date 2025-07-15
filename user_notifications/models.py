from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from django.utils.timezone import now
from wagtail.fields import RichTextField
from iogt.settings.base import AUTH_USER_MODEL
from django.contrib.auth import get_user_model
from notifications.models import Notification
@register_snippet
class UserNotificationTemplate(models.Model):
    NOTIFICATION_TYPES = [
        ("signup", "User Signup"),
        ("article", "Article Published"),
        ("survey", "Survey Published"),
        # add more types as needed
    ]

    type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        unique=True,  # optional: only one active per type
        help_text="Select the type of notification this template is used for."
    )
    title = models.CharField(max_length=255)
    message = RichTextField(features=["bold", "italic", "link", "ul", "ol"])
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(default=now)

    panels = [
        FieldPanel('title'),
        FieldPanel('message'),
        FieldPanel('active'),
        FieldPanel('type'),
    ]

    def __str__(self):
        return f"{self.title} ({'active' if self.active else 'inactive'})"

    class Meta:
        verbose_name = "User Notification Template"
        verbose_name_plural = "User Notification Templates"


class NotificationTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('ar', 'Arabic'),
    ]
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    receive_notifications = models.BooleanField(null=True, blank=True)  # NULL = not chosen yet
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    content_tags = models.ManyToManyField(NotificationTag, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"


User = get_user_model()
class NotificationLog(models.Model):
    STATE_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_key = models.CharField(max_length=255)  # e.g. template slug or key
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='sent')
    received_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.notification_key} → {self.user.username} [{self.state}]"

class NotificationMeta(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='meta')
    is_clicked = models.BooleanField(default=False)

