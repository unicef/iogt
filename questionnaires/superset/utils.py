from datetime import datetime

from copy import copy
from collections import Counter

from django.conf import settings
from django.utils import timezone

from home.models import SiteSettings
from questionnaires.models import UserSubmission
from questionnaires.superset.charts import (
    PieChart,
    BarChart,
    TableChart,
    BigNumberTotalChart,
    BigNumberTotalMeanChart,
    BigNumberTotalOpenEndedQuestionChart,
)
from questionnaires.superset.client import SupersetClient
from questionnaires.superset.dashboard import Dashboard
from questionnaires.superset.datasets import Dataset
from questionnaires.superset import ALLOWED_COLUMNS, ALLOWED_COLUMNS_REG_SURVEY

CHART_TYPE_MAP = {
    'checkbox': PieChart,
    'checkboxes': BarChart,
    'dropdown': BarChart,
    'email': TableChart,
    'singleline': BigNumberTotalOpenEndedQuestionChart,
    'multiline': BigNumberTotalOpenEndedQuestionChart,
    'number': BigNumberTotalMeanChart,
    'positivenumber': BigNumberTotalMeanChart,
    'radio': BarChart,
    'url': TableChart,
}

CALCULATED_COLUMN_EXPRESSION_MAP = {
    'checkbox': "((form_data::json)->'{}')::text",
    'checkboxes': "trim(both '\"' from json_array_elements((form_data::json)->'{}')::TEXT)",
    'dropdown': "trim(both '\"' from ((form_data::json)->'{}')::text)",
    'email': "trim(both '\"' from ((form_data::json)->'{}')::text)",
    'singleline': "((form_data::json)->'{}')::text",
    'multiline': "((form_data::json)->'{}')::text",
    'number': "(form_data::json->>'{}')::DECIMAL",
    'positivenumber': "(form_data::json->>'{}')::DECIMAL",
    'radio': "trim(both '\"' from ((form_data::json)->'{}')::text)",
    'url': "trim(both '\"' from ((form_data::json)->'{}')::text)",
}


class DashboardGenerator:
    def __init__(self, user, questionnaire, superset_username, superset_password):
        self.user = user
        self.questionnaire = questionnaire
        self.questions = questionnaire.get_form_fields().order_by('sort_order')
        self.client = SupersetClient()
        self.client.authenticate(superset_username, superset_password)
        self.admin_client = SupersetClient()
        self.admin_client.authenticate(settings.SUPERSET_USERNAME, settings.SUPERSET_PASSWORD)
        self.table_name = (
            "registration_survey"
            if questionnaire.slug in ["registration-survey", "wagtail-editing-survey-registration-survey"]
            else UserSubmission._meta.db_table
        )
        self.current_datetime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    def _get_database_id(self):
        resp = self.client.get_databases()
        for database in resp.get('result'):
            if database.get('database_name') == settings.SUPERSET_DATABASE_NAME:
                return database.get('id')
        raise Exception('No database found.')

    def _create_dashboard(self):
        dashboard = Dashboard(dashboard_title=f'{self.questionnaire.title} - {self.current_datetime}')
        resp = self.client.create_dashboard(data=dashboard.post_body())
        dashboard_id = resp.get('id')
        resp = self.client.get_dashboard(dashboard_id)
        result = resp.get('result', {})
        dashboard_url = result.get('url')
        owner_id = result.get('owners', [{}])[0].get('id')
        return dashboard_id, f'{settings.SUPERSET_BASE_URL}{dashboard_url}', owner_id

    def _create_dataset(self, database_id, owner_id):
        existing_dataset = self.admin_client.get_dataset_by_name(table_name=self.table_name, database_id=database_id)

        dataset_name = f'{SiteSettings.get_for_default_site()}_autodashboard_{self.questionnaire.__class__.__name__.lower()}_{self.questionnaire.id}_{self.questionnaire.title}_{self.current_datetime}'

        if existing_dataset:
            dataset_id = existing_dataset.get("id")
        else:
            dataset = Dataset(
                database_id=database_id, owner_id=owner_id, table_name=self.table_name, dataset_name=dataset_name,
                page_id=self.questionnaire.id)
            resp = self.admin_client.create_dataset(data=dataset.post_body())
            dataset_id = resp.get('id')

        dataset_detail = self.client.get_dataset(dataset_id)

        if self.questionnaire.slug == "registration-survey" or self.questionnaire.slug == "wagtail-editing-survey-registration-survey":
            columns = [{'column_name': column.get('column_name')} for column in
                       dataset_detail.get('result', {}).get('columns') if column.get('column_name') in ALLOWED_COLUMNS_REG_SURVEY]
        else:
            columns = [{'column_name': column.get('column_name')} for column in
                   dataset_detail.get('result', {}).get('columns') if column.get('column_name') in ALLOWED_COLUMNS]

        if self.questionnaire.slug != "registration-survey":
            for question in self.questions:
                calculated_column_expression = CALCULATED_COLUMN_EXPRESSION_MAP.get(question.field_type)
                if calculated_column_expression:
                    columns.append({
                        "column_name": question.label,
                        "expression": calculated_column_expression.format(question.clean_name),
                    })

        metrics = copy(dataset_detail.get('result', {}).get('metrics'))
        for metric in metrics:
            metric.pop('changed_on', None)
            metric.pop('created_on', None)
            metric.pop('uuid', None)

        if self.questionnaire.slug == "registration-survey" or self.questionnaire.slug == "wagtail-editing-survey-registration-survey":
            metrics.append({
                "expression": "SUM(count)",
                "metric_name": "response_count",
                "metric_type": "sum",
                "verbose_name": "Responses",
            })
        else:
            metrics.append({
                "expression": "COUNT(*)",
                "metric_name": "response_count",
                "metric_type": "count",
                "verbose_name": "Responses",
            })

        dataset = Dataset(
            database_id=database_id,
            owner_id=owner_id,
            table_name=self.table_name,
            dataset_name=dataset_name,
            page_id=self.questionnaire.id
        )

        self.admin_client.update_dataset(id=dataset_id, data=dataset.put_body(columns, metrics))
        return dataset_id

    def _create_charts(self, dashboard_id, dataset_id):
        chart = BigNumberTotalChart(dashboard_id=dashboard_id, dataset_id=dataset_id, name='Total Submissions')
        self.client.create_chart(data=chart.post_body())

        if self.questionnaire.slug == "registration-survey" or self.questionnaire.slug == "wagtail-editing-survey-registration-survey":
            bar_chart = BarChart(
                dashboard_id=dashboard_id,
                dataset_id=dataset_id,
                name='Age Category vs Gender',
                x_axis='age_category',
                y_axis='gender',
                series='response_count'
            )
            self.client.create_chart(data=bar_chart.post_body())
        else:
            for question in self.questions:
                chart_class = CHART_TYPE_MAP.get(question.field_type)
                if chart_class:
                    chart = chart_class(
                        dashboard_id=dashboard_id, dataset_id=dataset_id, name=question.label,
                        clean_name=question.clean_name)
                    self.client.create_chart(data=chart.post_body())

    def generate(self):
        if self.questionnaire.slug == "registration-survey" or self.questionnaire.slug == "wagtail-editing-survey-registration-survey":
            SurveyDataProcessor.generate_aggregated_data(self.questionnaire.id)

        database_id = self._get_database_id()
        dashboard_id, dashboard_url, owner_id = self._create_dashboard()
        dataset_id = self._create_dataset(database_id, owner_id)
        self._create_charts(dashboard_id, dataset_id)
        return dashboard_url


from django.db import connection


class SurveyDataProcessor:
    # Mapping common gender variations to standardized categories
    GENDER_MAPPING = {
        "male": "Male", "man": "Male", "men": "Male", "masculine": "Male",
        "female": "Female", "woman": "Female", "women": "Female", "feminine": "Female",
        "non-binary": "Non-Binary", "Other": "Non-Binary", "Third": "Non-Binary"
    }

    @staticmethod
    def calculate_age(date_of_birth: str) -> int:
        if not date_of_birth:  # Handle None or empty date_of_birth
            return None  # Return None explicitly to handle in get_age_category

        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
            today = datetime.today()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except (ValueError, TypeError):
            return None  # Return None for invalid dates

    @staticmethod
    def get_age_category(age: int) -> str:
        if age is None:  # Handle missing DOB case
            return "No Age Category Data"

        AGE_CATEGORIES = [
            ("Youth", 0, 19),
            ("Adult", 20, 39),
            ("Senior", 40, 59),
            ("Elder", 60, 99)
        ]
        for category_name, min_age, max_age in AGE_CATEGORIES:
            if min_age <= age <= max_age:
                return category_name
        return "Unknown"

    @staticmethod
    def normalize_gender(gender: str) -> str:
        if not gender:  # Handle None or empty gender cases
            return "No Gender Data"

        gender = gender.strip().lower()  # Standardize case and remove spaces
        return SurveyDataProcessor.GENDER_MAPPING.get(gender, "Unknown")  # Default to "Other" if not mapped

    @staticmethod
    def aggregate_submission_data(page_id: int):
        submissions = UserSubmission.objects.filter(page_id=page_id)
        if not submissions.exists():
            return []  # Return an empty list if no data

        data_list = []

        for submission in submissions:
            form_data = submission.form_data
            date_of_birth = form_data.get("date_of_birth", "")
            gender = form_data.get("gender", "")

            normalized_gender = SurveyDataProcessor.normalize_gender(gender)  # Normalize gender input
            age = SurveyDataProcessor.calculate_age(date_of_birth)
            age_category = SurveyDataProcessor.get_age_category(age)

            data_list.append((age_category, normalized_gender))

        data_counter = Counter(data_list)
        return [{"age_category": age, "gender": gender, "count": count} for (age, gender), count in
                data_counter.items()]

    @staticmethod
    def generate_aggregated_data(page_id: int):
        aggregated_data = SurveyDataProcessor.aggregate_submission_data(page_id)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM registration_survey")
            if aggregated_data:  # Avoid inserting empty data
                for row in aggregated_data:
                    cursor.execute(
                        "INSERT INTO registration_survey (age_category, gender, count) VALUES (%s, %s, %s)",
                        [row['age_category'], row['gender'], row['count']]
                    )
