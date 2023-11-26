from requests import Session, Request
from rest_framework import status


class MoyaPayClient:
    BASE_URL = 'https://payments.api.dev.moyapayd.app'
    customer_url = f'{BASE_URL}/customers'
    merchant_url = f'{BASE_URL}/merchants'
    merchant_token_url = f'{merchant_url}/tokens/validate'
    merchant_wallet_url = f'{merchant_url}/wallet'
    pay_customer_url = f'{customer_url}/pay'

    def __init__(self):
        self.session = Session()
        self.access_token = ''

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def _get_validated_response(self, response):
        if response.ok:
            return response.json()
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            raise Exception('Unauthorised - Invalid or no authentication token supplied')
        else:
            raise Exception(f'Something went wrong. Status: {response.status_code}')

    def _api_caller(self, request):
        request = self.session.prepare_request(request)
        response = self.session.send(request)
        return self._get_validated_response(response)

    def authenticate(self):
        request = Request(method='GET', url=self.merchant_token_url, headers=self._get_headers())
        self._api_caller(request)

    def get_merchant_balance(self):
        request = Request(method='GET', url=self.merchant_wallet_url, headers=self._get_headers())
        return self._api_caller(request).get('balance')

