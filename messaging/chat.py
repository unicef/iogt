import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone
from webpush import send_user_notification

from .models import Message, Thread, UserThread
from messaging.rapidpro_client import RapidProClient

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatManager:
    def __init__(self, thread):
        if thread is None:
            raise Exception('No thread found.')
        self.thread = thread

    def _record_message_in_database(self, sender, rapidpro_message_id, text, quick_replies, is_chatbot_message):
        # Messages sent from User to RapidPro server don't have rapidpro_message_id
        from_rapidpro_server = bool(rapidpro_message_id)

        if from_rapidpro_server:
            message, created = Message.objects.get_or_create(rapidpro_message_id=rapidpro_message_id, defaults={
                'sender': sender,
                'text': text,
                'quick_replies': quick_replies,
                'thread': self.thread,
                "is_chatbot_message": is_chatbot_message,
            })

            if not created:
                # If the message already exists, we concatenate the newly received
                # messages with the existing message. An assumption here is that
                # messages will always be received in the correct order. This should
                # be confirmed with RapidPro
                message.text = f'{message.text}{text}'
                message.save(update_fields=['text'])
            else:
                payload = {
                    'head': 'New Message!',
                    'body': 'Click here to view it.',
                    'url': self.thread.get_absolute_url(),
                }
                for user in self.thread.users.all():
                    try:
                        send_user_notification(user=user, payload=payload, ttl=1000)
                    except Exception as e:
                        logger.exception(e)

        else:
            Message.objects.create(
                rapidpro_message_id=rapidpro_message_id, sender=sender, text=text, thread=self.thread,
                quick_replies=quick_replies)

        self.thread.last_message_at = timezone.now()
        self.thread.save(update_fields=['last_message_at'])

    def _handle_attachments(self, message):
        cleaned_text, attachment_links = ChatManager._parse_rapidpro_message(message.text)
        message.text = cleaned_text
        message.update_or_create_attachments(attachment_links)
        message.save()

    @staticmethod
    def _parse_rapidpro_message(message_text):
        message_parts = message_text.split('\n')
        attachments = []
        cleaned_message = ""
        for message in reversed(message_parts):
            validator = URLValidator()
            try:
                validator(message)
                attachments.append(message)
            except ValidationError:
                cleaned_message = f'{message}{cleaned_message}'
        return cleaned_message, attachments

    def record_reply(self, text, sender, rapidpro_message_id=None, quick_replies=None, mark_unread=True, is_chatbot_message=False):
        if quick_replies is None:
            quick_replies = []
        if sender.is_rapidpro_bot_user and not rapidpro_message_id:
            client = RapidProClient(self.thread)
            client.send_reply(text)

        self._record_message_in_database(
            sender=sender, rapidpro_message_id=rapidpro_message_id, text=text, quick_replies=quick_replies, is_chatbot_message=is_chatbot_message)

        if mark_unread:
            self.thread.mark_unread(sender)

    @staticmethod
    def initiate_thread(sender, recipients, chatbot, subject, text):
        sender_thread = UserThread.objects.filter(user=sender, thread__chatbot=chatbot).first()

        if sender_thread:
            thread = sender_thread.thread
        else:
            thread = Thread.objects.create(subject=subject, chatbot=chatbot)

            user_threads = []
            for user in recipients + [sender]:
                user_threads.append(UserThread(user=user, thread=thread))
            UserThread.objects.bulk_create(user_threads)

        chat_manager = ChatManager(thread)
        chat_manager.record_reply(sender=sender, text=text)

        thread.mark_unread(sender)
        return thread
