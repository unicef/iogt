from rest_framework import serializers


class RapidProMessageSerializer(serializers.Serializer):
    id = serializers.CharField()
    content = serializers.CharField()
    to = serializers.UUIDField()
    from_ = serializers.UUIDField(required=False)
    channel = serializers.UUIDField()
    quick_replies = serializers.JSONField()

    def get_fields(self):
        fields = super().get_fields()
        fields['from'] = fields.pop('from_')
        return fields
