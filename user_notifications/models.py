from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from django.utils.timezone import now
from wagtail.fields import RichTextField
from iogt.settings.base import AUTH_USER_MODEL
from django.contrib.auth import get_user_model
from notifications.models import Notification
from wagtailautocomplete.edit_handlers import AutocompletePanel


class UserNotificationTemplate(models.Model):
    NOTIFICATION_TYPES = [
        ("signup", "User Signup"),
        ("article", "Article Published"),
        ("survey", "Survey Published"),
        ("section", "Section Published"),
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
    
    autocomplete_search_field = 'name'

    def autocomplete_label(self):
        return self.name

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
    
    panels = [
        AutocompletePanel('user', target_model='iogt_users.User'),
        FieldPanel("receive_notifications"),
        FieldPanel("preferred_language"),
        AutocompletePanel('content_tags', target_model='user_notifications.NotificationTag'),
    ]

    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"


User = get_user_model()


class NotificationLog(models.Model):
    STATE_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    notification = models.OneToOneField(Notification, null=True, blank=True, on_delete=models.SET_NULL, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_key = models.CharField(max_length=255)  # e.g. template slug or key
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='sent')
    received_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.notification_key} → {self.user.username} [{self.state}]"


class NotificationMeta(models.Model):
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='meta')
    is_clicked = models.BooleanField(default=False)

