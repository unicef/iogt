from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RapidProMessageSerializer
from ..chat import ChatManager
from ..models import Thread

User = get_user_model()


class RapidProWebhook(APIView):

    # TODO: Add basic authentication in authentication_classes
    def post(self, request):
        print(request.data)
        serializer = RapidProMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        thread_uuid = serializer.validated_data['to']
        text = serializer.validated_data['text']

        thread = Thread.objects.get(uuid=thread_uuid)
        # TODO: Decide how to treat each of these potential errors:
        # - Invalid thread UUID
        # - channel UUID mismatch

        # TODO: Stitch Messages
        # TODO: Extract attachments from messages.



        chat_manager = ChatManager(thread)
        chat_manager.record_reply(sender=User.get_rapidpro_bot_user(), text=text)

        return Response(data='ok', status=status.HTTP_200_OK)
