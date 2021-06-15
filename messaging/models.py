from urllib import request, parse
import json
import uuid
import re

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .signals import message_sent
from .utils import cached_attribute


class ChatbotChannel(models.Model):
    identifier = models.CharField(max_length=30)
    display_name = models.CharField(max_length=80)
    request_url = models.URLField(max_length=200)

    def channel_uuid(self):
        # TODO: Validate the format of the URL in the entry form.
        # Otherwise this method may throw an exception.
        return uuid.UUID(re.search('^https?://.+/c/ex/([0-9a-fA-F\-]*)/receive$', self.request_url).group(1))

    def __str__(self):
        return f"{self.display_name}: {self.identifier}, {self.request_url}"



class Thread(models.Model):

    subject = models.CharField(max_length=150)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through="UserThread")
    chatbot = models.ForeignKey(ChatbotChannel, on_delete=models.PROTECT)
    uuid = models.UUIDField(default=uuid.uuid4)

    @classmethod
    def inbox(cls, user):
        return cls.objects.filter(userthread__user=user, userthread__deleted=False)

    @classmethod
    def deleted(cls, user):
        return cls.objects.filter(userthread__user=user, userthread__deleted=True)

    @classmethod
    def unread(cls, user):
        return cls.objects.filter(
            userthread__user=user,
            userthread__deleted=False,
            userthread__unread=True
        )

    def __str__(self):
        return f"{self.subject}: {self.chatbot.display_name} {', '.join([str(user) for user in self.users.all()])}"

    def get_absolute_url(self):
        return reverse("messaging:thread_detail", args=[self.pk])

    @property
    @cached_attribute
    def first_message(self):
        return self.messages.all()[0]

    @property
    @cached_attribute
    def latest_message(self):
        return self.messages.order_by("-sent_at")[0]

    @classmethod
    def ordered(cls, objs):
        """
        Returns the iterable ordered the correct way, this is a class method
        because we don"t know what the type of the iterable will be.
        """
        objs = list(objs)
        objs.sort(key=lambda o: o.latest_message.sent_at, reverse=True)
        return objs


class UserThread(models.Model):

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    unread = models.BooleanField()
    deleted = models.BooleanField()


class Message(models.Model):

    thread = models.ForeignKey(Thread, related_name="messages", on_delete=models.CASCADE)

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="sent_messages", on_delete=models.CASCADE)
    # If sent_from_bot is True, the sender is ignored and instead the chatbot
    # that's in the thread is considered as the sender.
    # TODO: Is there an automatic way on entry creation/modification
    # to validate that sender must not be null if sent_from_bot is False?
    sent_from_bot = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now)

    content = models.TextField()
    # If sent from RapidPro, the ID the message has in RapidPro.
    rapid_pro_message_id = models.IntegerField(null=True)
    # Attachments and quick replies are encoded as a json string
    # TODO: Decide if we want to use a different format?
    # E.g. django.contrib.postgres.fields.ArrayField
    # or models.JSONField(default=lambda x:[])
    quick_replies = models.TextField(default="[]")
    attachments = models.TextField(default="[]")

    @classmethod
    def http_request_to_rapidpro(cls, thread, user, content):
        # TODO: This should be async or queued somewhere and the responses should be
        # checked, for proper processing to ensure all requests are successful.
        data = parse.urlencode({"from": thread.uuid, "text": content}).encode()
        req = request.Request(thread.chatbot.request_url, data=data)
        resp = request.urlopen(req)

    @classmethod
    def new_reply_to_rapidpro(cls, thread, user, content):
        """
        Create a new reply for an existing Thread and send it to RapidPro.
        """
        Message.http_request_to_rapidpro(thread, user, content)
        return Message.new_reply(thread, user, content)

    @classmethod
    def new_reply(cls, thread, user, content,
            sent_from_bot=False,
            rapid_pro_message_id=None,
            quick_replies="[]",
            attachments="[]"):
        """
        Create a new reply for an existing Thread.

        Mark thread as unread for all other participants, and
        mark thread as read by replier.
        """
        msg = cls.objects.create(
                thread=thread,
                sender=user,
                content=content,
                sent_from_bot=sent_from_bot,
                rapid_pro_message_id=rapid_pro_message_id,
                quick_replies=quick_replies,
                attachments=attachments)
        if not sent_from_bot:
            assert user is not None
            thread.userthread_set.exclude(user=user).update(deleted=False, unread=True)
            thread.userthread_set.filter(user=user).update(deleted=False, unread=False)
        message_sent.send(sender=cls, message=msg, thread=thread, reply=True)
        return msg

    @classmethod
    def new_message(cls, from_user, to_users, chatbot, subject, content):
        """
        Create a new Message and Thread.

        Mark thread as unread for all recipients, and
        mark thread as read and deleted from inbox by creator.
        """
        thread = Thread.objects.create(subject=subject, chatbot=chatbot)
        for user in to_users:
            thread.userthread_set.create(user=user, deleted=False, unread=True)
        thread.userthread_set.create(user=from_user, deleted=True, unread=False)
        msg = cls.objects.create(thread=thread, sender=from_user, content=content)
        Message.http_request_to_rapidpro(thread, from_user, content)
        message_sent.send(sender=cls, message=msg, thread=thread, reply=False)
        return msg

    class Meta:
        ordering = ("sent_at",)

    def get_absolute_url(self):
        return self.thread.get_absolute_url()
    
    def quick_replies_list(self):
        return json.loads(self.quick_replies)
