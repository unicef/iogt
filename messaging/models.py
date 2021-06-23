from urllib import request, parse
import json
import uuid
import re

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .querysets import ThreadQuerySet


class ChatbotChannel(models.Model):
    identifier = models.CharField(max_length=30)
    display_name = models.CharField(max_length=80)
    request_url = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.display_name}: {self.identifier}, {self.request_url}"


class Thread(models.Model):
    subject = models.CharField(max_length=150)
    users = models.ManyToManyField(get_user_model(), through="UserThread")
    chatbot = models.ForeignKey('ChatbotChannel', on_delete=models.PROTECT)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    last_message_at = models.DateTimeField(null=True, editable=False, default=None)

    objects = models.Manager()
    thread_objects = ThreadQuerySet.as_manager()

    def mark_unread(self, sender=None):
        """
        Mark all related UserThread(s) unread
        """
        if sender:
            self.user_threads.exclude(user=sender).update(is_read=False)
            self.user_threads.filter(user=sender).update(is_read=True)
        else:
            self.user_threads.update(is_read=False)

    def __str__(self):
        return f"{self.subject}: {self.chatbot.display_name} {', '.join([str(user) for user in self.users.all()])}"

    def get_absolute_url(self):
        return reverse("messaging:thread_detail", args=[self.pk])


class UserThread(models.Model):
    thread = models.ForeignKey('Thread', related_name='user_threads', on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)


class Message(models.Model):
    thread = models.ForeignKey('Thread', related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(), null=True, related_name="sent_messages", on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    content = models.TextField()
    # If sent from RapidPro, the ID the message has in RapidPro.
    rapidpro_message_id = models.IntegerField(null=True)
    # Attachments and quick replies are encoded as a json string

    quick_replies = models.JSONField(default=list)
    attachments = models.JSONField(default=list)

    class Meta:
        ordering = ("sent_at",)

    def get_absolute_url(self):
        return self.thread.get_absolute_url()
