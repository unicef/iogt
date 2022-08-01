import logging
from abc import ABC

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


class BaseModerator(ABC):
    @classmethod
    def is_valid(cls, comment):
        raise NotImplementedError


class HiveModerator(BaseModerator):
    hive_api = 'https://api.thehive.ai/api/v2/task/sync'
    severity_threshold = 3  # Severity score at which text is flagged or moderated, configurable.
    restricted_classes = ['sexual', 'hate', 'violence', 'bullying', 'spam']  # Select classes to monitor

    @classmethod
    def _get_headers(cls):
        return {'Authorization': f'Token {settings.HIVE_MODERATION_API_KEY}'}

    @classmethod
    def _validate_response(cls, response):
        if response.ok:
            return response.json()

        raise Exception('Invalid response from Hive')

    @classmethod
    def _get_hive_response(cls, text):
        headers = cls._get_headers()
        data = {'text_data': text}  # Must be a string. This is also where you would insert metadata if desired.
        return requests.post(cls.hive_api, headers=headers, data=data)

    @classmethod
    def _handle_hive_classifications(cls, response):
        # Create a dictionary where the classes are keys and the scores their respective values.
        scores_dict = {x['class']: x['score'] for x in response['status'][0]['response']['output'][0]['classes']}
        for restricted_class in cls.restricted_classes:
            if scores_dict[restricted_class] >= cls.severity_threshold:
                return False

        return True

    @classmethod
    def is_valid(cls, comment):
        try:
            response = cls._get_hive_response(comment.comment)
            response = cls._validate_response(response)
            return cls._handle_hive_classifications(response)
        except Exception as e:
            logger.error(f'Error response from hive moderation.')
            return True


class StubModerator(BaseModerator):
    @classmethod
    def is_valid(cls, comment):
        return True
