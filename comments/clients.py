import logging
from abc import ABC

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class BaseModerator(ABC):
    def __init__(self, comment):
        self.comment = comment

    def is_valid(self):
        raise NotImplementedError


class HiveModerator(BaseModerator):
    hive_api = 'https://api.thehive.ai/api/v2/task/sync'
    severity_threshold = 3  # Severity score at which text is flagged or moderated, configurable.
    restricted_classes = ['sexual', 'hate', 'violence', 'bullying', 'spam']  # Select classes to monitor

    def _get_headers(self):
        return {'Authorization': f'Token {settings.HIVE_MODERATION_API_KEY}'}

    def _validate_response(self, response):
        if response.ok:
            return response.json()

        logger.error(f'Error response from hive moderation.')

    def _get_hive_response(self):
        headers = self._get_headers()
        data = {'text_data': self.comment.comment}  # Must be a string. This is also where you would insert metadata if desired.
        return requests.post(self.hive_api, headers=headers, data=data)

    def _handle_hive_classifications(self, response):
        # Create a dictionary where the classes are keys and the scores their respective values.
        scores_dict = {x['class']: x['score'] for x in response['status'][0]['response']['output'][0]['classes']}
        for restricted_class in self.restricted_classes:
            if scores_dict[restricted_class] >= self.severity_threshold:
                return False

        return True

    def is_valid(self):
        response = self._get_hive_response()
        response = self._validate_response(response)
        return self._handle_hive_classifications(response)


class StubModerator(BaseModerator):
    def is_valid(self):
        return True
