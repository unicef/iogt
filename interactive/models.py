from django.db import models
from django.utils.translation import gettext_lazy as _

class InteractiveChannel(models.Model):
    display_name = models.CharField(
        max_length=80,
        help_text=_('Name for the interactive bot that the user will seen when interacting with it'),
    )
    request_url = models.URLField(
        max_length=200,
        help_text=_('To set up a interactive bot channel on your RapidPro server and get a request URL, '
                    'follow the steps outline in the Section "Setting up a Chatbot channel" '
                    'here: https://github.com/unicef/iogt/blob/develop/messaging/README.md'),
    )

    # Plan on adding trigger words

    def __str__(self):
        return f"{self.display_name}, {self.request_url}"

class Message(models.Model):
    rapidpro_message_id = models.AutoField(primary_key=True)
    text = models.TextField()
    quick_replies = models.JSONField(null=True, blank=True)
    to = models.CharField(max_length=255)
    from_field = models.CharField(max_length=255)
    channel = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'RapidPro {self.rapidpro_id}'
