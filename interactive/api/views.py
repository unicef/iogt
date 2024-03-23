from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView
from interactive.models import Message
from rest_framework import status
from .serializers import RapidProMessageSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsRapidProGroupUser

class RapidProWebhook(APIView):
    permission_classes = [IsAuthenticated, IsRapidProGroupUser]

    def post(self, request):
        serializer = RapidProMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data from serializer
        rapidpro_message_id = serializer.validated_data.get('id')
        to = serializer.validated_data.get('to')
        text = serializer.validated_data.get('text')
        quick_replies = serializer.validated_data.get('quick_replies')
        from_field = serializer.validated_data.get('from')
        channel = serializer.validated_data.get('channel')

        # Get the latest message for the 'to' recipient
        prev_msg = Message.objects.filter(to=to).order_by('-created_at').first()

        # Update or create a new message
        if prev_msg:
            prev_msg_text = prev_msg.text.strip()

            if prev_msg_text.endswith('[CONTINUE]'):
                text = prev_msg_text + text
            else:
                text = text
                
            fields_to_update = {
                'rapidpro_message_id': rapidpro_message_id,
                'text': text,
                'quick_replies': quick_replies,
                'updated_at': now(),
            }
            Message.objects.filter(rapidpro_message_id=prev_msg.rapidpro_message_id).update(**fields_to_update)
        else:
            # Create a new message
            message_data = {
                'rapidpro_message_id': rapidpro_message_id,
                'text': text,
                'quick_replies': quick_replies,
                'to': to,
                'from_field': from_field,
                'channel': channel,
                'created_at': now(),
                'updated_at': now()
            }
            Message.objects.create(**message_data)

        return Response(data='ok', status=status.HTTP_200_OK)