from rest_framework import serializers
from wagtail.core.models import Page


class QuestionnairePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title']
