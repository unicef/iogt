import re
import time
import uuid

import requests
from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

from home.mixins import PageUtilsMixin, TitleIconMixin
from interactive.forms import MessageSendForm
from interactive.services import ShortCodeService


class InteractiveChannel(models.Model):
    display_name = models.CharField(
        max_length=80,
        help_text=_(
            "Name for the interactive bot that the user will seen when interacting with it"
        ),
    )
    request_url = models.URLField(
        max_length=200,
        help_text=_(
            "To set up a interactive bot channel on your RapidPro server and get a request URL, "
            'follow the steps outline in the Section "Setting up a Chatbot channel" '
            "here: https://github.com/unicef/iogt/blob/develop/messaging/README.md"
        ),
    )

    def __str__(self):
        return f"{self.display_name}, {self.request_url}"


class Message(models.Model):
    rapidpro_message_id = models.BigIntegerField(primary_key=True)
    text = models.TextField()
    quick_replies = models.JSONField(null=True, blank=True)
    to = models.CharField(max_length=255)
    from_field = models.CharField(max_length=255)
    channel = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class InteractivePage(Page, PageUtilsMixin, TitleIconMixin):
    parent_page_types = ["home.HomePage", "home.Section", "home.FooterIndexPage"]
    subpage_types = []
    template = "interactive/interactive_game.html"

    trigger_string = models.CharField(max_length=255)
    channel = models.ForeignKey(InteractiveChannel, on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        FieldPanel("trigger_string"),
        FieldPanel("channel"),
    ]

    def __str__(self):
        return self.title

    def serve(self, request, *args, **kwargs):
        if request.session.session_key is None:
            request.session.save()
        self.session = request.session

        user = self.get_user_identifier(request)

        if not user:
            return redirect("/")
        
        if request.method == "GET":
            chat = Message.objects.filter(to=user).order_by("-created_at").first()
            if not chat:
                self.send_message_to_rapidpro(user=user, text=self.trigger_string)

        if request.method == "POST":
            form = MessageSendForm(request.POST)

            if form.is_valid():
                self.send_message_to_rapidpro(user=user, text=form.cleaned_data["text"])

                return redirect(self.get_url(request))

            return redirect(request.META.get("HTTP_REFERER", "/"))

        self.send_message_on_language_switch(request, user)

        context = self.get_context(request)
        context["db_data"] = self.get_message_from_db(user=user)

        if not context["db_data"]:
            return redirect("/")

        return render(request, self.template, context)

    def get_user_identifier(self, request):
        if not request.session.session_key:
            request.session.save()

        user_uuid = request.session.setdefault("interactive_uuid", str(uuid.uuid4()))
        user = request.user

        if user.is_authenticated:
            if user.interactive_uuid:
                user_uuid = user.interactive_uuid
            else:
                user_model = get_user_model()
                user.interactive_uuid = user_uuid
                user_model.objects.filter(pk=user.pk).update(interactive_uuid=user_uuid)

        return user_uuid

    def get_message_from_db(self, user):
        # Wait to receive new message from rapidpro
        time.sleep(1)

        start_time = time.time()

        while True:
            # Elapsed time in seconds
            elapsed_time = time.time() - start_time

            if elapsed_time >= 5:
                break

            chat = Message.objects.filter(to=user).order_by("-created_at").first()
            if not chat:
                return None

            text = chat.text.strip()

            if text.endswith("[CONTINUE]"):
                time.sleep(1)
            else:
                break

        shortcode_service = ShortCodeService()
        text = shortcode_service.apply_shortcode(text)
        pattern = r'\[color_scheme\s+bg-color="(?P<bg_color>[^"]+)"(\])?'
        match = re.search(pattern, text)
        bg_color = match.group("bg_color") if match else ""

        # Remove the [bg_color] tag from the input string
        text = re.sub(pattern, "", text)

        return {
            "message": text,
            "buttons": chat.quick_replies,
            "bg_color": bg_color,
        }

    def send_message_on_language_switch(self, request, user):
        current_lang = request.build_absolute_uri().split("/")[3]

        if request.META.get("HTTP_REFERER"):
            referer_lang = request.META.get("HTTP_REFERER").split("/")[3]
        else:
            referer_lang = current_lang

        if referer_lang != current_lang:
            self.send_message_to_rapidpro(user=user, text=self.trigger_string)

    def send_message_to_rapidpro(self, user, text):
        data = {"from": user, "text": text}

        try:
            response = requests.post(url=self.channel.request_url, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return redirect("/")