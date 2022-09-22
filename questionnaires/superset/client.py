from django.conf import settings
from django.utils import timezone
from requests import Session, Request
from rest_framework import status

from home.models import SiteSettings
from questionnaires.models import UserSubmission
from questionnaires.superset.dashboard import Dashboard
from questionnaires.superset.charts import CHART_TYPE_MAP, TotalSubmissionsChart
from questionnaires.superset.datasets import Dataset


class SupersetClient:
    api_url = f'{settings.SUPERSET_BASE_URL}/api/v1'
    security_url = f'{api_url}/security'
    login_url = f'{security_url}/login'
    refresh_url = f'{security_url}/refresh'
    csrf_token_url = f'{security_url}/csrf_token'
    database_url = f'{api_url}/database'
    dashboard_url = f'{api_url}/dashboard'
    dataset_url = f'{api_url}/dataset'
    chart_url = f'{api_url}/chart'
    session = Session()

    def _get_csrf_token(self):
        return {
            'X_CSRFToken': self.csrf_token,
        }

    def _get_auth_headers(self):
        return {
            'Authorization': f"Bearer {self.access_token}",
        }

    def _get_headers(self):
        headers = self._get_auth_headers()
        headers.update(self._get_csrf_token())
        return headers

    def _get_validated_response(self, response):
        if response.ok:
            return response.json()
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise Exception('Unauthorized: Invalid username or password.')
        else:
            raise Exception('Something went wrong.')

    def _api_caller(self, request):
        request = self.session.prepare_request(request)
        response = self.session.send(request)
        return self._get_validated_response(response)

    def authenticate(self, username, password):
        data = {
            'username': username,
            'password': password,
            'refresh': True,
            'provider': 'db',
        }
        request = Request(method='POST', url=self.login_url, json=data)
        response = self._api_caller(request)
        self.access_token = response.get('access_token')
        self.refresh_token = response.get('refresh_token')

        request = Request(method='GET', url=self.csrf_token_url, headers=self._get_auth_headers())
        response = self._api_caller(request)
        self.csrf_token = response.get('result')

    def get_databases(self):
        request = Request(method='GET', url=self.database_url, headers=self._get_headers())
        return self._api_caller(request)

    def create_dashboard(self, data):
        request = Request(method='POST', url=self.dashboard_url, headers=self._get_headers(), json=data)
        return self._api_caller(request)

    def create_dataset(self, data):
        request = Request(method='POST', url=self.dataset_url, headers=self._get_headers(), json=data)
        return self._api_caller(request)

    def update_dataset(self, id, data):
        request = Request(method='PUT', url=f'{self.dataset_url}/{id}', headers=self._get_headers(), json=data)
        return self._api_caller(request)

    def create_chart(self, data):
        request = Request(method='POST', url=f'{self.chart_url}', headers=self._get_headers(), json=data)
        return self._api_caller(request)


class DashboardGenerator:
    def __init__(self, user, questionnaire, superset_username, superset_password):
        self.user = user
        self.questionnaire = questionnaire
        self.superset_username = superset_username
        self.superset_password = superset_password

    def generate(self):
        client = SupersetClient()
        client.authenticate(self.superset_username, self.superset_password)
        database_resp = client.get_databases()
        database_id = None
        for database in database_resp.get('result'):
            if database['database_name'] == settings.SUPERSET_DATABASE_NAME:
                database_id = database.get('id')

        dashboard = Dashboard(dashboard_title=self.questionnaire.title)
        dashboard_resp = client.create_dashboard(data=dashboard.post_body)
        dashboard_id = dashboard_resp['id']
        dataset_name = f'{SiteSettings.get_for_default_site()}_autodashboard_' \
                       f'{self.questionnaire.__class__.__name__.lower()}_{self.questionnaire.id}_' \
                       f'{self.questionnaire.title}_{timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
        dataset = Dataset(
            database_id=database_id, table_name=UserSubmission._meta.db_table, dataset_name=dataset_name,
            page_id=self.questionnaire.id)
        dataset_post_resp = client.create_dataset(data=dataset.post_body)
        dataset_id = dataset_post_resp['id']
        client.update_dataset(id=dataset_id, data=dataset.put_body)
        chart = TotalSubmissionsChart(dashboard_id=dashboard_id, dataset_id=dataset_id, name='Total Submissions')
        client.create_chart(data=chart.post_body)
        for question in self.questionnaire.get_form_fields():
            chart_class = CHART_TYPE_MAP.get(question.field_type)
            if chart_class:
                chart = chart_class(
                    dashboard_id=dashboard_id, dataset_id=dataset_id, name=question.label,
                    clean_name=question.clean_name)
                client.create_chart(data=chart.post_body)
