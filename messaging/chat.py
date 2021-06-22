from django.utils import timezone

from .models import Message, Thread, UserThread
from messaging.rapidpro_client import RapidProClient


class ChatManager:
    def __init__(self, thread=None):
        self.thread = thread

    def create_rapidpro_reply(self, text, sender):
        if not self.thread:
            raise Exception('No thread found.')
        client = RapidProClient(self.thread)
        client.send_reply(text)
        Message.objects.create(thread=self.thread, sender=sender, content=text)
        self.thread.last_message_at = timezone.now()
        self.thread.save(update_fields=['last_message_at'])

    def create_reply(self, text, sender):
        self.create_rapidpro_reply(sender, text)
        self.thread.mark_unread(sender)

    @classmethod
    def initiate_thread(cls, sender, recipients, chatbot, subject, text):
        thread = Thread.objects.create(subject=subject, chatbot=chatbot)

        chat_manager = cls(thread)
        chat_manager.create_rapidpro_reply(sender, text)

        user_threads = []
        for user in recipients + [sender]:
            user_threads.append(UserThread(user=user, thread=thread))
        UserThread.objects.bulk_create(user_threads)

        thread.mark_unread(sender)
        return thread
