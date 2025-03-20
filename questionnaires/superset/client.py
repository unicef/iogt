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

    def _get_params(self):
        return {
            'override_columns': 'true'
        }

    def _get_validated_response(self, response):
        if response.ok:
            return response.json()
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise Exception('Unauthorized: Invalid username or password.')
        else:
            raise Exception(f'Something went wrong. Status: {response.status_code}')

    def _api_caller(self, request):
        request = self.session.prepare_request(request)
        print(f"URL: {request.url}")
        print(f"Method: {request.method}")
        print(f"Headers: {request.headers}")
        if request.body:
            print(f"Body: {request.body}")
        response = self.session.send(request)

        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55")
        print("Received Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Body: {response.text}")
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
        request = Request(method='PUT', url=f'{self.dataset_url}{id}', params=self._get_params(), headers=self._get_headers(), json=data)
        return self._api_caller(request)

    def create_chart(self, data):
        request = Request(method='POST', url=f'{self.chart_url}', headers=self._get_headers(), json=data)
        return self._api_caller(request)

    def get_dataset_by_name(self, table_name, database_id):
        """Fetch a dataset by table_name and manually filter by database_id."""
        query = {
            "filters": [
                {"col": "table_name", "opr": "eq", "value": table_name}
            ]
        }
        import json
        url = f"{self.dataset_url}?q={json.dumps(query)}"
        request = Request(method='GET', url=url, headers=self._get_headers())
        response = self._api_caller(request)

        datasets = response.get("result", [])
        if not datasets:
            return None  # No matching dataset found

        # Manually filter datasets by database_id
        filtered_datasets = [dataset for dataset in datasets if dataset.get('database').get('id') == database_id]
        if not filtered_datasets:
            return None  # No dataset matches the table_name and database_id

        return filtered_datasets[0]  # Return the first matching dataset
