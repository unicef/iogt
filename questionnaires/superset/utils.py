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
        self.superset_username = superset_username
        self.superset_password = superset_password

    def generate(self):
        client = SupersetClient()
        client.authenticate(self.superset_username, self.superset_password)

        database_resp = client.get_databases()
        database_id = None
        for database in database_resp.get('result'):
            if database.get('database_name') == settings.SUPERSET_DATABASE_NAME:
                database_id = database.get('id')
        assert database_id is not None

        dashboard = Dashboard(dashboard_title=self.questionnaire.title)
        dashboard_id = client.create_dashboard(data=dashboard.post_body()).get('id')

        dataset_name = f'{SiteSettings.get_for_default_site()}_autodashboard_' \
                       f'{self.questionnaire.__class__.__name__.lower()}_{self.questionnaire.id}_' \
                       f'{self.questionnaire.title}_{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
        dataset = Dataset(
            database_id=database_id, table_name=UserSubmission._meta.db_table, dataset_name=dataset_name,
            page_id=self.questionnaire.id)
        dataset_id = client.create_dataset(data=dataset.post_body()).get('id')

        dataset_detail = client.get_dataset(dataset_id)
        columns = copy(dataset_detail.get('result', {}).get('columns'))
        for column in columns:
            column.pop('changed_on', None)
            column.pop('created_on', None)
            column.pop('type_generic', None)
            column.pop('uuid', None)

        for question in self.questions:
            calculated_column_expression = CALCULATED_COLUMN_EXPRESSION_MAP.get(question.field_type)
            if calculated_column_expression:
                columns.append({
                    "column_name": question.clean_name,
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
        client.update_dataset(id=dataset_id, data=dataset.put_body(columns, metrics))

        chart = BigNumberTotalChart(dashboard_id=dashboard_id, dataset_id=dataset_id, name='Total Submissions')
        client.create_chart(data=chart.post_body())

        for question in self.questions:
            chart_class = CHART_TYPE_MAP.get(question.field_type)
            if chart_class:
                chart = chart_class(
                    dashboard_id=dashboard_id, dataset_id=dataset_id, name=question.label,
                    clean_name=question.clean_name)
                client.create_chart(data=chart.post_body())
