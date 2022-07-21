import json

from rest_framework import serializers
from wagtail.core.models import Page

from questionnaires.models import (
    Survey,
    SurveyFormField,
    Poll,
    PollFormField,
    QuizFormField,
    Quiz,
    UserSubmission,
)


class QuestionnairePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title']


class PollFormFieldSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices and instance.choices.split('|')

    class Meta:
        model = PollFormField
        fields = [
            'id', 'sort_order', 'label', 'clean_name', 'help_text', 'required', 'field_type', 'choices',
            'default_value', 'admin_label',
        ]


class PollPageDetailSerializer(serializers.ModelSerializer):
    description = serializers.JSONField(source='description.stream_data')
    thank_you_text = serializers.JSONField(source='thank_you_text.stream_data')
    terms_and_conditions = serializers.JSONField(source='terms_and_conditions.stream_data')
    url = serializers.CharField(source='full_url')
    published_at = serializers.DateTimeField(source='last_published_at')
    questions = PollFormFieldSerializer(source='poll_form_fields', many=True)

    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'live', 'url', 'published_at', 'allow_anonymous_submissions',
            'allow_multiple_submissions', 'show_results', 'result_as_percentage', 'randomise_options',
            'show_results_with_no_votes', 'submit_button_text', 'direct_display', 'index_page_description',
            'index_page_description_line_2', 'description', 'thank_you_text', 'terms_and_conditions',
            'questions',
        ]


class SurveyFormFieldSerializer(serializers.ModelSerializer):
    skip_logic = serializers.JSONField(source='skip_logic.stream_data')

    class Meta:
        model = SurveyFormField
        fields = [
            'id', 'sort_order', 'label', 'clean_name', 'help_text', 'required', 'field_type', 'skip_logic',
            'default_value', 'admin_label', 'page_break',
        ]


class SurveyPageDetailSerializer(serializers.ModelSerializer):
    description = serializers.JSONField(source='description.stream_data')
    thank_you_text = serializers.JSONField(source='thank_you_text.stream_data')
    terms_and_conditions = serializers.JSONField(source='terms_and_conditions.stream_data')
    url = serializers.CharField(source='full_url')
    published_at = serializers.DateTimeField(source='last_published_at')
    questions = SurveyFormFieldSerializer(source='survey_form_fields', many=True)

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'live', 'url', 'published_at', 'allow_anonymous_submissions',
            'allow_multiple_submissions', 'submit_button_text', 'direct_display', 'index_page_description',
            'index_page_description_line_2', 'multi_step', 'description', 'thank_you_text', 'terms_and_conditions',
            'questions',
        ]


class QuizFormFieldSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices.split('|')

    class Meta:
        model = QuizFormField
        fields = [
            'id', 'sort_order', 'label', 'clean_name', 'help_text', 'required', 'field_type', 'choices',
            'default_value', 'correct_answer', 'feedback', 'admin_label', 'page_break',
        ]


class QuizPageDetailSerializer(serializers.ModelSerializer):
    description = serializers.JSONField(source='description.stream_data')
    thank_you_text = serializers.JSONField(source='thank_you_text.stream_data')
    terms_and_conditions = serializers.JSONField(source='terms_and_conditions.stream_data')
    url = serializers.CharField(source='full_url')
    published_at = serializers.DateTimeField(source='last_published_at')
    questions = QuizFormFieldSerializer(source='quiz_form_fields', many=True)

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'live', 'url', 'published_at', 'allow_anonymous_submissions',
            'allow_multiple_submissions', 'submit_button_text', 'direct_display', 'index_page_description',
            'index_page_description_line_2', 'multi_step', 'description', 'thank_you_text', 'terms_and_conditions',
            'questions',
        ]


class QuestionnairePageDetailSerializer(serializers.Serializer):
    poll = PollPageDetailSerializer()
    survey = SurveyPageDetailSerializer()
    quiz = QuizPageDetailSerializer()


class UserSubmissionSerializer(serializers.ModelSerializer):
    submission = serializers.SerializerMethodField()
    user = serializers.CharField()
    page_url = serializers.CharField(source='page.full_url')

    def get_submission(self, instance):
        return json.loads(instance.form_data)

    class Meta:
        model = UserSubmission
        fields = ['id', 'user', 'submit_time', 'page_url', 'submission']
