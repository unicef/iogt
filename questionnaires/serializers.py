import json

from rest_framework import serializers
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.core.models import Page

from questionnaires.models import (
    Survey,
    SurveyFormField,
    Poll,
    PollFormField,
    QuizFormField,
    Quiz,
    UserSubmission,
    QuestionnairePage,
)


class QuestionnairePageSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='content_type.model')

    class Meta:
        model = Page
        fields = ['id', 'title', 'type', 'last_published_at']


class BaseFormFieldSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()
    default_value = serializers.SerializerMethodField()

    def get_choices(self, instance):
        return instance.choices and instance.choices.split('|')

    def get_default_value(self, instance):
        return instance.default_value and instance.default_value.split('|')

    class Meta:
        model = AbstractFormField
        fields = [
            'id', 'sort_order', 'label', 'clean_name', 'help_text', 'required', 'field_type', 'choices',
            'default_value',
        ]
        abstract = True


class BaseQuestionnairePageDetailSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    thank_you_text = serializers.SerializerMethodField()
    terms_and_conditions = serializers.SerializerMethodField()
    url = serializers.CharField(source='full_url')

    def get_description(self, obj):
        if obj.description:
            return [d for d in obj.description.raw_data]
        return []

    def get_thank_you_text(self, obj):
        if obj.thank_you_text:
            return [d for d in obj.thank_you_text.raw_data]
        return []

    def get_terms_and_conditions(self, obj):
        if obj.terms_and_conditions:
            return [d for d in obj.terms_and_conditions.raw_data]
        return []

    class Meta:
        model = QuestionnairePage
        fields = [
            'id', 'title', 'last_published_at', 'live', 'url', 'last_published_at', 'allow_anonymous_submissions',
            'allow_multiple_submissions', 'submit_button_text', 'direct_display', 'index_page_description',
            'index_page_description_line_2', 'description', 'thank_you_text', 'terms_and_conditions',
        ]
        abstract = True


class PollFormFieldSerializer(BaseFormFieldSerializer):
    class Meta:
        model = PollFormField
        fields = BaseFormFieldSerializer.Meta.fields + ['admin_label']


class PollPageDetailSerializer(BaseQuestionnairePageDetailSerializer):
    questions = PollFormFieldSerializer(source='poll_form_fields', many=True)

    class Meta:
        model = Poll
        fields = BaseQuestionnairePageDetailSerializer.Meta.fields + [
            'show_results', 'result_as_percentage', 'randomise_options', 'show_results_with_no_votes', 'questions',
        ]


class SurveyFormFieldSerializer(BaseFormFieldSerializer):
    skip_logic = serializers.SerializerMethodField()

    def get_skip_logic(self, obj):
        if obj.skip_logic:
            return [d for d in obj.skip_logic.raw_data]
        return []

    class Meta:
        model = SurveyFormField
        fields = BaseFormFieldSerializer.Meta.fields + ['skip_logic', 'admin_label', 'page_break']


class SurveyPageDetailSerializer(BaseQuestionnairePageDetailSerializer):
    questions = SurveyFormFieldSerializer(source='survey_form_fields', many=True)

    class Meta:
        model = Survey
        fields = BaseQuestionnairePageDetailSerializer.Meta.fields + ['multi_step', 'questions']


class QuizFormFieldSerializer(BaseFormFieldSerializer):
    correct_answer = serializers.SerializerMethodField()

    def get_correct_answer(self, instance):
        return instance.correct_answer and instance.correct_answer.split('|')

    class Meta:
        model = QuizFormField
        fields = BaseFormFieldSerializer.Meta.fields + ['correct_answer', 'feedback', 'admin_label', 'page_break']


class QuizPageDetailSerializer(BaseQuestionnairePageDetailSerializer):
    questions = QuizFormFieldSerializer(source='quiz_form_fields', many=True)

    class Meta:
        model = Quiz
        fields = BaseQuestionnairePageDetailSerializer.Meta.fields + ['multi_step', 'questions']


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
            question = instance.page.specific.get_form_fields().filter(clean_name=clean_name).first()
            if question:
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
