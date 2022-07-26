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
    type = serializers.CharField(source='content_type.model')

    class Meta:
        model = Page
        fields = ['id', 'title', 'type', 'last_published_at']


class PollFormFieldSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()
    default_value = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices and instance.choices.split('|')

    def get_default_value(self, instance):
        return instance.default_value and instance.default_value.split('|')

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
    choices = serializers.SerializerMethodField()
    default_value = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices and instance.choices.split('|')

    def get_default_value(self, instance):
        return instance.default_value and instance.default_value.split('|')

    skip_logic = serializers.JSONField(source='skip_logic.stream_data')

    class Meta:
        model = SurveyFormField
        fields = [
            'id', 'sort_order', 'label', 'clean_name', 'help_text', 'required', 'field_type', 'choices', 'skip_logic',
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
    default_value = serializers.SerializerMethodField()
    correct_answer = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices and instance.choices.split('|')

    def get_default_value(self, instance):
        return instance.default_value and instance.default_value.split('|')

    def get_correct_answer(self, instance):
        return instance.correct_answer and instance.correct_answer.split('|')

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
        form_data = json.loads(instance.form_data)
        form_data_ = []
        for clean_name, answer in form_data.items():
            question = instance.page.specific.get_form_fields().get(clean_name=clean_name)
            form_data_.append({
                question.admin_label: {
                    "clean_name": clean_name,
                    "user_answer": answer,
                }
            })
        return form_data_

    class Meta:
        model = UserSubmission
        fields = ['id', 'user', 'submit_time', 'page_url', 'submission']
