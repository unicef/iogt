from django.urls import path
from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.core import hooks

from questionnaires.admin import PollAdmin
from questionnaires.admin_views import PollResultsAdminView


@hooks.register("register_admin_urls")
def register_question_results_admin_view_url():
    return [
        path(
            "polls/question/<parent>/results/",
            PollResultsAdminView.as_view(),
            name="question-results-admin",
        ),
    ]


modeladmin_register(PollAdmin)
