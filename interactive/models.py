import re
from time import sleep
import time
import uuid
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
import requests
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from home.mixins import PageUtilsMixin, TitleIconMixin
from django.contrib.auth import get_user_model

from interactive.forms import MessageSendForm
from interactive.services import ShortCodeService


# from interactive.services import ShortCodeService


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


class InteractivePage(Page, PageUtilsMixin, TitleIconMixin):
    parent_page_types = [
        "home.HomePage", "home.Section", 'home.FooterIndexPage'
    ]
    subpage_types = []
    template = 'interactive/interactive_game.html'

    # button_text = models.CharField(max_length=255)
    trigger_string = models.CharField(max_length=255)
    channel = models.ForeignKey(
        InteractiveChannel,
        on_delete=models.PROTECT
    )

    content_panels = Page.content_panels + [
        # FieldPanel('button_text'),
        FieldPanel('trigger_string'),
        FieldPanel('channel'),
    ]

    def __str__(self):
        return self.title

    def serve(self, request, *args, **kwargs):
        if request.session.session_key is None:
            request.session.save()
        self.session = request.session

        user = self.get_user_identifier(request)

        if not user:
            return redirect('/')

        if request.method == "POST":
            form = MessageSendForm(request.POST)

            if form.is_valid():
                channel_url = self.channel.request_url

                data = {
                    'from': user,
                    'text': form.cleaned_data['text']
                }

                try:
                    response = requests.post(url=channel_url, data=data)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    return redirect('/')

                return redirect(self.get_url(request))

            return redirect(request.META.get('HTTP_REFERER', '/'))

        self.send_message_on_language_switch(request, user)

        context = self.get_context(request)
        context['db_data'] = self.get_message_from_db(user=user)

        if not context['db_data']:
            return redirect('/')

        return render(request, self.template, context)

    def get_user_identifier(self, request):
        if not request.session.session_key:
            request.session.save()

        user_uuid = request.session.setdefault('interactive_uuid', str(uuid.uuid4()))

        # Get the authenticated user
        user = request.user

        # If the user is authenticated and has no 'interactive_uuid' set, update it
        if user.is_authenticated:
            if user.interactive_uuid:
                user_uuid = user.interactive_uuid
            else:
                user_model = get_user_model()
                user.interactive_uuid = user_uuid
                user_model.objects.filter(pk=user.pk).update(interactive_uuid=user_uuid)

        return user_uuid

    def get_message_from_db(self, user):
        # wait a second to receive new message from rapidpro
        time.sleep(1)

        start_time = time.time()

        while True:
            # Calculate the elapsed time
            elapsed_time = time.time() - start_time

            # Break the loop if 5 seconds have elapsed
            if elapsed_time >= 5:
                break

            chat = Message.objects.filter(to=user).order_by('-created_at').first()
            if not chat:
                return None

            text = chat.text.strip()

            # Check if the message has a next message indicator
            if text.endswith('[CONTINUE]'):
                time.sleep(1)
            else:
                break  # Exit the loop if the message does not end with '[CONTINUE]'

        shortcode_service = ShortCodeService()
        text = shortcode_service.apply_shortcode(text)

        # Define the regular expression pattern
        pattern = r'\[color_scheme\s+bg-color="(?P<bg_color>[^"]+)"(\])?'

        # Search for matches in the input string
        match = re.search(pattern, text)

        bg_color = ''
        # Check if a match is found
        if match:
            # Extract the bg_color attributes
            bg_color = match.group('bg_color')

        # Remove the [bg_color] tag from the input string
        text = re.sub(pattern, '', text)

        return {
            'message': text,
            'buttons': chat.quick_replies,
            'bg_color': bg_color,
        }

    def send_message_on_language_switch(self, request, user):
        current_lang = request.build_absolute_uri().split('/')[3]

        if request.META.get('HTTP_REFERER'):
            referer_lang = request.META.get('HTTP_REFERER').split('/')[3]
        else:
            referer_lang = current_lang

        if referer_lang != current_lang:
            data = {
                'from': user,
                'text': self.trigger_string
            }

            response = requests.post(url=self.channel.request_url, data=data)
