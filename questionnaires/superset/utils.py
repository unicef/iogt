from copy import copy

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
from questionnaires.superset import ALLOWED_COLUMNS

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
    'checkbox': "unistr(((form_data::json)->'{}')::text)",
    'checkboxes': "unistr(trim(both '\"' from json_array_elements((form_data::json)->'{}')::text))",
    'dropdown': "unistr(trim(both '\"' from ((form_data::json)->'{}')::text))",
    'email': "unistr(trim(both '\"' from ((form_data::json)->'{}')::text))",
    'singleline': "unistr(((form_data::json)->'{}')::text)",
    'multiline': "unistr(((form_data::json)->'{}')::text)",
    'number': "(form_data::json->>'{}')::DECIMAL",
    'positivenumber': "(form_data::json->>'{}')::DECIMAL",
    'radio': "unistr(trim(both '\"' from ((form_data::json)->'{}')::text))",
    'url': "unistr(trim(both '\"' from ((form_data::json)->'{}')::text))",
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
        self.table_name = UserSubmission._meta.db_table
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
        if existing_dataset:
            dataset_id = existing_dataset.get("id")
            print(f"Dataset already exists with ID: {dataset_id}")
        else:
            print("heloooooooooooooooooooooooooooooooooooooooooooooooooooo")
            dataset_name = f'{SiteSettings.get_for_default_site()}_autodashboard_' \
                           f'{self.questionnaire.__class__.__name__.lower()}_{self.questionnaire.id}_' \
                           f'{self.questionnaire.title}_{self.current_datetime}'
            dataset = Dataset(
                database_id=database_id, owner_id=owner_id, table_name=self.table_name, dataset_name=dataset_name,
                page_id=self.questionnaire.id)
            resp = self.admin_client.create_dataset(data=dataset.post_body())
            dataset_id = resp.get('id')

        dataset_detail = self.client.get_dataset(dataset_id)

        columns = [
            {'column_name': column.get('column_name')}
            for column in dataset_detail.get('result', {}).get('columns')
            if column.get('column_name') in ALLOWED_COLUMNS
        ]

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

        metrics.append({
            "expression": "COUNT(*)",
            "metric_name": "response_count",
            "metric_type": "count",
            "verbose_name": "Responses",
        })

        dataset_name = f'{SiteSettings.get_for_default_site()}_autodashboard_' \
                       f'{self.questionnaire.__class__.__name__.lower()}_{self.questionnaire.id}_' \
                       f'{self.questionnaire.title}_{self.current_datetime}'

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

        for question in self.questions:
            chart_class = CHART_TYPE_MAP.get(question.field_type)
            if chart_class:
                chart = chart_class(
                    dashboard_id=dashboard_id, dataset_id=dataset_id, name=question.label,
                    clean_name=question.clean_name)
                self.client.create_chart(data=chart.post_body())

    def generate(self):
        database_id = self._get_database_id()
        dashboard_id, dashboard_url, owner_id = self._create_dashboard()
        dataset_id = self._create_dataset(database_id, owner_id)
        self._create_charts(dashboard_id, dataset_id)

        return dashboard_url
