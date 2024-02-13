import logging, requests


class RapidProApiService(object):
    ACCESS_TOKEN = 'Token 3599dfede6caf725712581703f8ff5928f3fd1c9'
    RAPID_URL = 'https://rapidpro.rultest2.com'

    def __init__(self):
        pass

    def get_current_contact(self, user: object = None):
        response = requests.get(
            f'{self.RAPID_URL}/api/v2/flows.json',
            params={'urn': f'ext:{user}'},
            headers={'Authorization': self.ACCESS_TOKEN},
        )

        if len(response.json().get('results')) < 1:
            data = {
                "name": "Cranky User",
                "urns": [f"ext:{user}"]
            }
            response = requests.post(
                f'{self.RAPID_URL}/api/v2/flows.json',
                headers={'Authorization': self.ACCESS_TOKEN},
                json=data,
            )
        return response.json().get('results')[0] if response.json().get('results') else None

    def send_message(self, data=None):
        url = f'{self.RAPID_URL}/c/ex/e22f30ce-8a14-46da-b8b7-478966c4ba1c/receive'
        headers = {'Authorization': self.ACCESS_TOKEN}

        try:
            response = requests.post(url=url, headers=headers, data=data)
            response.raise_for_status()
            logging.info(f'Send message: {response.text}')
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f'Error sending message: {e}')
            return None


