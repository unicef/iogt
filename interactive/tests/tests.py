from django.test import TestCase
from uuid import uuid4
from rest_framework.test import APITestCase, APIClient
from django.core import management
from home.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse

from interactive.models import Message


# Create your tests here.
class RapidProWebhookTest(APITestCase):
    def setUp(self) -> None:
        username = uuid4()
        management.call_command('sync_rapidpro_bot_user', username=username)
        self.bot_user = User.objects.get(username=username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.bot_user).access_token}')

    def test_webhook_stitches_messages(self):

        rapidpro_data_list = [
            {
                "id": "1",
                "text": "Some message with the first part of text. First part ends at the exclamation mark!",
                "to": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },
            {
                "id": "1",
                "text": "The second part starts here",
                "to": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "from": "abcd",
                "channel": "bd3577c6-65b1-4bb7-9611-306c11b1dcc5",
                "quick_replies": [
                    "Baby (0 to 23 months old)", "Young child (2 to 9 years)", "Teenager (10 to 17 years)"
                ]
            },

        ]

        for data in rapidpro_data_list:
            response = self.client.post(path=reverse('interactive_api:rapidpro_message_webhook'), data=data, format='json')

        message = Message.objects.first()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.text, 'The second part starts here')
        self.assertEqual(len(message.quick_replies), 3)
