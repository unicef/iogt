from base64 import b64encode

from django.core import management
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from home.models import User
from messaging.factories import ThreadFactory
from messaging.models import Message


class RapidProWebhookTest(APITestCase):
    @override_settings(RAPIDPRO_BOT_USER_USERNAME='rb1', RAPIDPRO_BOT_USER_PASSWORD='rapidpassword1')
    def setUp(self) -> None:
        management.call_command('sync_rapidpro_bot_user')
        self.bot_user = User.objects.first()
        self.client.credentials(HTTP_AUTHORIZATION="Basic {}".format(
            b64encode(bytes(f"rb1:rapidpassword1", "utf-8")).decode("ascii")
        ))

    @override_settings(RAPIDPRO_BOT_USER_USERNAME='rb1', RAPIDPRO_BOT_USER_PASSWORD='rapidpassword1')
    def test_webhook_parses_attachments(self):
        thread = ThreadFactory()

        rapidpro_data = {
            "id": "1",
            "text": "Some message with attachment.\nhttps://rapidpro.idems.international/media/attachments/43/"
                    "15890/steps/3de4f80a-1eab-42db-8b7e-d7c35edecd06.bin",
            "to": str(thread.uuid),
            "from": "abcd",
            "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
            "quick_replies": [
                "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"]}

        response = self.client.post(path=reverse('messaging:api:rapidpro_webhook'), data=rapidpro_data, format='json')

        message = Message.objects.first()
        attachment = message.attachments.all()[0]

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.attachments.all().count(), 1)
        self.assertEqual(message.text, 'Some message with attachment.')
        self.assertEqual(attachment.external_link,
                         'https://rapidpro.idems.international/media/attachments/43/15890/steps/'
                         '3de4f80a-1eab-42db-8b7e-d7c35edecd06.bin')
        self.assertIsNotNone(attachment.file)
