from rest_framework import serializers
from .models import RapidPro


class RapidProSerializer(serializers.ModelSerializer):

    class Meta:
        model = RapidPro
        fields = ['rapidpro_id', 'text', 'quick_replies', 'to', 'from_field', 'channel']
