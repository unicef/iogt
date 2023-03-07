import json

from rest_framework import serializers

from questionnaires.models import (
    UserSubmission,
)


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
                    "admin_label": question.admin_label,
                    "clean_name": clean_name,
                    "user_answer": answer,
                })
        return form_data_

    class Meta:
        model = UserSubmission
        fields = ['id', 'user', 'submit_time', 'page_url', 'submission']
        ref_name = "User Submission V2"
