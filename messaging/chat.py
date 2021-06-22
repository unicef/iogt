from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Message, Thread, UserThread
from messaging.rapidpro_client import RapidProClient

User = get_user_model()


class ChatManager:
    def __init__(self, thread):
        if thread is None:
            raise Exception('No thread found.')
        self.thread = thread

    def _record_message_in_database(self, sender, text):
        Message.objects.create(thread=self.thread, sender=sender, content=text)
        self.thread.last_message_at = timezone.now()
        self.thread.save(update_fields=['last_message_at'])

    def record_reply(self, text, sender, mark_unread=True):
        if not sender.is_rapidpro_bot_user:
            client = RapidProClient(self.thread)
            client.send_reply(text)

        self._record_message_in_database(sender=sender, text=text)

        if mark_unread:
            self.thread.mark_unread(sender)

    @classmethod
    def initiate_thread(cls, sender, recipients, chatbot, subject, text):
        thread = Thread.objects.create(subject=subject, chatbot=chatbot)

        chat_manager = cls(thread)
        chat_manager.create_rapidpro_reply(sender=sender, text=text)

        user_threads = []
        for user in recipients + [sender]:
            user_threads.append(UserThread(user=user, thread=thread))
        UserThread.objects.bulk_create(user_threads)

        thread.mark_unread(sender)
        return thread
