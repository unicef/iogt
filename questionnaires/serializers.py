from rest_framework import serializers
from wagtail.core.models import Page

from questionnaires.models import Survey, SurveyFormField, Poll, PollFormField, QuizFormField, Quiz


class QuestionnairePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title']


class PollFormFieldSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices.split('|')

    class Meta:
        model = PollFormField
        fields = '__all__'


class PollPageDetailSerializer(serializers.ModelSerializer):
    questions = PollFormFieldSerializer(source='poll_form_fields', many=True)

    class Meta:
        model = Poll
        fields = '__all__'


class SurveyFormFieldSerializer(serializers.ModelSerializer):
    skip_logic = serializers.JSONField(source='skip_logic.stream_data')

    class Meta:
        model = SurveyFormField
        fields = '__all__'


class SurveyPageDetailSerializer(serializers.ModelSerializer):
    description = serializers.JSONField(source='description.stream_data')
    thank_you_text = serializers.JSONField(source='thank_you_text.stream_data')
    terms_and_conditions = serializers.JSONField(source='terms_and_conditions.stream_data')
    questions = SurveyFormFieldSerializer(source='survey_form_fields', many=True)

    class Meta:
        model = Survey
        fields = '__all__'


class QuizFormFieldSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices.split('|')

    class Meta:
        model = QuizFormField
        fields = '__all__'


class QuizPageDetailSerializer(serializers.ModelSerializer):
    description = serializers.JSONField(source='description.stream_data')
    thank_you_text = serializers.JSONField(source='thank_you_text.stream_data')
    terms_and_conditions = serializers.JSONField(source='terms_and_conditions.stream_data')
    questions = QuizFormFieldSerializer(source='quiz_form_fields', many=True)

    class Meta:
        model = Quiz
        fields = '__all__'
