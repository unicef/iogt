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

    def _record_message_in_database(self, sender, rapidpro_message_id, text, quick_replies):
        # Messages sent from User to RapidPro server don't have rapidpro_message_id
        if rapidpro_message_id:
            message, created = Message.objects.get_or_create(rapidpro_message_id=rapidpro_message_id, defaults={
                'sender': sender,
                'text': text,
                'quick_replies': quick_replies,
                'thread': self.thread,
            })
            if not created:
                # If the message already exists, we concatenate the newly received
                # messages with the existing message. An assumption here is that
                # messages will always be received in the correct order. This should
                # be confirmed with RapidPro
                message.text = f'{message.text} {text}'
                message.save(update_fields=['text'])
        else:
            Message.objects.create(
                rapidpro_message_id=rapidpro_message_id, sender=sender, text=text, thread=self.thread,
                quick_replies=quick_replies)

        self.thread.last_message_at = timezone.now()
        self.thread.save(update_fields=['last_message_at'])

    def record_reply(self, text, sender, rapidpro_message_id=None, quick_replies=None, mark_unread=True):
        if quick_replies is None:
            quick_replies = []
        if not sender.is_rapidpro_bot_user:
            client = RapidProClient(self.thread)
            client.send_reply(text)

        self._record_message_in_database(
            sender=sender, rapidpro_message_id=rapidpro_message_id, text=text, quick_replies=quick_replies)

        if mark_unread:
            self.thread.mark_unread(sender)

    @staticmethod
    def initiate_thread(sender, recipients, chatbot, subject, text):
        thread = Thread.objects.create(subject=subject, chatbot=chatbot)

        chat_manager = ChatManager(thread)
        chat_manager.record_reply(sender=sender, text=text)

        user_threads = []
        for user in recipients + [sender]:
            user_threads.append(UserThread(user=user, thread=thread))
        UserThread.objects.bulk_create(user_threads)

        thread.mark_unread(sender)
        return thread
