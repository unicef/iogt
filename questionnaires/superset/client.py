from django.conf import settings
from requests import Session, Request
from rest_framework import status


class SupersetClient:
    api_url = f'{settings.SUPERSET_BASE_URL}/api/v1'
    security_url = f'{api_url}/security'
    login_url = f'{security_url}/login'
    refresh_url = f'{security_url}/refresh'
    csrf_token_url = f'{security_url}/csrf_token/'
    database_url = f'{api_url}/database/'
    dashboard_url = f'{api_url}/dashboard/'
    dataset_url = f'{api_url}/dataset/'
    chart_url = f'{api_url}/chart/'

    def __init__(self):
        self.session = Session()

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
            raise Exception(f'Something went wrong. Status: {response.status_code}')

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

    def get_dashboard(self, id):
        request = Request(method='GET', url=f'{self.dashboard_url}{id}', headers=self._get_auth_headers())
        return self._api_caller(request)

    def create_dataset(self, data):
        request = Request(method='POST', url=self.dataset_url, headers=self._get_headers(), json=data)
        return self._api_caller(request)

    def get_dataset(self, id):
        request = Request(method='GET', url=f'{self.dataset_url}{id}', headers=self._get_headers())
        return self._api_caller(request)

    def update_dataset(self, id, data):
        request = Request(method='PUT', url=f'{self.dataset_url}{id}', headers=self._get_headers(), json=data)
        return self._api_caller(request)

    def create_chart(self, data):
        request = Request(method='POST', url=f'{self.chart_url}', headers=self._get_headers(), json=data)
        return self._api_caller(request)
