import json
from pathlib import Path

from django.test import TestCase
from iogt_content_migration.management.commands.fix_surveys import create_field
from questionnaires.factories import SurveyFactory


class TestFixSurveys(TestCase):
    def test_create_form_field(self):
        survey = SurveyFactory()

        with open(open_resource("v1_page_revision_survey_form_field.json")) as fp:
            field = create_field(survey, json.load(fp))

        self.assertEqual(len(field.skip_logic), 2)

        option = field.skip_logic[0].value
        self.assertEqual(option["choice"], "Yes")
        self.assertEqual(option["skip_logic"], "next")
        self.assertIsNone(option["question"])

        self.assertEqual(
            field.choices,
            "All of this information is new to me|"
            "Most of this information is new to me|"
            "A little bit of this information is new to me|"
            "None of of this information is new to me",
        )
        self.assertEqual(field.page.id, survey.id)


def open_resource(filename):
    return Path(__file__).parent / "resources" / filename
