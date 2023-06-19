import json
from django.urls import reverse

from iogt_users.factories import AdminUserFactory
from questionnaires.factories import SurveyFactory, SurveyFormFieldFactory
from selenium_tests.base import BaseSeleniumTests
from selenium_tests.pages import WagtailAdminPage


class AdminPanelSeleniumTests(BaseSeleniumTests):
    def setUp(self):
        self.setup_blank_site()
        admin_user = AdminUserFactory()
        self.visit_login_page().login_user(admin_user)
        self.survey01 = SurveyFactory(
            parent=self.home,
            owner=admin_user,
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )

    def test_skip_logic_validation_errors_on_admin_panel(self):
        SurveyFormFieldFactory(label='Q1', page=self.survey01, required=True, field_type='checkbox')
        SurveyFormFieldFactory(label='Q2', page=self.survey01, required=True, field_type='checkbox')
        SurveyFormFieldFactory(label='Q3', page=self.survey01, required=True, field_type='checkbox')

        self.visit_url(reverse('wagtailadmin_pages:edit', args=(self.survey01.id,)))

        admin_page = WagtailAdminPage(self.selenium)
        admin_page.skip_to_question(question=0, skip_logic=0, skip_to=3)
        admin_page.submit_response()

        self.assertIn(
            "Skip to question Q3 with in-between required questions isn't allowed.",
            self.selenium.page_source
        )

    def test_skip_logic_requires_multi_step_enabled_on_admin_panel(self):
        skip_logic = json.dumps(
            [
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "true",
                        "skip_logic": "end",
                        "question": None
                    }
                },
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "false",
                        "skip_logic": "next",
                        "question": None
                    }
                }
            ]
        )
        SurveyFormFieldFactory(label='Q1', page=self.survey01, required=True, field_type='checkbox',
                               skip_logic=skip_logic)
        SurveyFormFieldFactory(label='Q2', page=self.survey01, required=True, field_type='checkbox',
                               skip_logic=skip_logic)

        self.visit_url(reverse('wagtailadmin_pages:edit', args=(self.survey01.id,)))
        admin_page = WagtailAdminPage(self.selenium)
        admin_page.submit_response()

        self.assertIn(
            "Multi-step is required to properly display questionnaires that include Skip Logic.",
            self.selenium.page_source
        )
