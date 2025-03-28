import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .permissions import IsRapidProGroupUser
from .serializers import RapidProMessageSerializer
from ..chat import ChatManager
from ..models import Thread

User = get_user_model()


class RapidProWebhook(APIView):
    permission_classes = [IsAuthenticated, IsRapidProGroupUser]

    def post(self, request):
        serializer = RapidProMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rapidpro_message_id = serializer.validated_data['id']
        thread_uuid = serializer.validated_data['to']
        text = serializer.validated_data['text']
        quick_replies = serializer.validated_data['quick_replies']

        thread = get_object_or_404(Thread, uuid=thread_uuid)

        chat_manager = ChatManager(thread)
        chat_manager.record_reply(
            sender=request.user, text=text, quick_replies=quick_replies,
            rapidpro_message_id=rapidpro_message_id, is_chatbot_message=True)

        return Response(data='ok', status=status.HTTP_200_OK)
