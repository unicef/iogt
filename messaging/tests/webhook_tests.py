from uuid import uuid4

from django.core import management
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from home.models import User
from messaging.factories import ThreadFactory
from messaging.models import Message, Attachment


class RapidProWebhookTest(APITestCase):
    def setUp(self) -> None:
        username = uuid4()
        management.call_command('sync_rapidpro_bot_user', username=username)
        self.bot_user = User.objects.get(username=username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.bot_user).access_token}')

    def test_webhook_stitches_messages(self):
        thread = ThreadFactory()

        rapidpro_data_list = [
            {
                "id": "1",
                "text": "Some message with the first part of text. First part ends at the exclamation mark!",
                "to": str(thread.uuid),
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },
            {
                "id": "1",
                "text": "The second part starts here",
                "to": str(thread.uuid),
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },

        ]

        for data in rapidpro_data_list:
            response = self.client.post(path=reverse('messaging:api:rapidpro_webhook'), data=data, format='json')

        message = Message.objects.first()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.text, 'Some message with the first part of text.'
                                       ' First part ends at the exclamation mark!The second part starts here')
        self.assertEqual(len(message.quick_replies), 3)

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

        message = thread.get_renderable_messages().first()
        attachment = message.attachments.all()[0]

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.attachments.all().count(), 1)
        self.assertEqual(message.text, 'Some message with attachment.')
        self.assertEqual(attachment.external_link,
                         'https://rapidpro.idems.international/media/attachments/43/15890/steps/'
                         '3de4f80a-1eab-42db-8b7e-d7c35edecd06.bin')
        self.assertIsNotNone(attachment.file)

    def test_stitched_attachment_parsing(self):
        thread = ThreadFactory()

        rapidpro_data_list = [
            {
                "id": "1",
                "text": "Some message with a stitched url. \nhttps://via.placeholder.com/200",
                "to": str(thread.uuid),
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },
            {
                "id": "1",
                "text": "678910.jpg",
                "to": str(thread.uuid),
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },

        ]

        for data in rapidpro_data_list:
            response = self.client.post(path=reverse('messaging:api:rapidpro_webhook'), data=data, format='json')

        message = thread.get_renderable_messages().first()
        attachment = message.attachments.first()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.text, 'Some message with a stitched url. ')
        self.assertEqual(message.attachments.count(), 1)
        self.assertEqual(attachment.external_link, 'https://via.placeholder.com/200678910.jpg')
        self.assertEqual(len(message.quick_replies), 3)

    def test_single_download(self):
        thread = ThreadFactory()

        rapidpro_data_list = [
            {
                "id": "1",
                "text": "Some message with attachment \nhttps://via.placeholder.com/200",
                "to": str(thread.uuid),
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },
            {
                "id": "2",
                "text": "Another message with the same attachment \nhttps://via.placeholder.com/200",
                "to": str(thread.uuid),
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },

        ]

        for data in rapidpro_data_list:
            response = self.client.post(path=reverse('messaging:api:rapidpro_webhook'), data=data, format='json')

        messages = thread.get_renderable_messages()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].text, 'Another message with the same attachment ')
        self.assertEqual(messages[1].text, 'Some message with attachment ')
        self.assertEqual(Attachment.objects.count(), 1)

        attachment = Attachment.objects.first()
        self.assertEqual('https://via.placeholder.com/200', attachment.external_link)

        self.assertIsNotNone(attachment.image)
