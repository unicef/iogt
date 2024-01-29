import requests
from django.db import models
from django.utils.translation import gettext_lazy as _


class CrankyUncleChannel(models.Model):
    display_name = models.CharField(
        max_length=80,
        help_text=_('Name for the cranky uncle bot that the user will seen when interacting with it'),
    )
    request_url = models.URLField(
        max_length=200,
        help_text=_('To set up a cranky uncle bot channel on your RapidPro server and get a request URL, '
                    'follow the steps outline in the Section "Setting up a Chatbot channel" '
                    'here: https://github.com/unicef/iogt/blob/develop/messaging/README.md'),
    )

    # Plan on adding trigger words

    def __str__(self):
        return f"{self.display_name}, {self.request_url}"
