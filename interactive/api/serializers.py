from rest_framework import serializers


class RapidProMessageSerializer(serializers.Serializer):
    channel = serializers.UUIDField(required=False)
    from_ = serializers.CharField()
    id = serializers.CharField()
    quick_replies = serializers.JSONField()
    text = serializers.CharField()
    to = serializers.UUIDField()

    def get_fields(self):
        fields = super().get_fields()
        fields["from"] = fields.pop("from_")
        return fields
