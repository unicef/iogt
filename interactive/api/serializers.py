from rest_framework import serializers


class RapidProMessageSerializer(serializers.Serializer):
    channel = serializers.UUIDField()
    from_ = serializers.CharField(required=False)
    id = serializers.CharField()
    quick_replies = serializers.JSONField()
    text = serializers.CharField()
    to = serializers.UUIDField()
