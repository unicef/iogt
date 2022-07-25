from abc import ABC

import requests
from django.conf import settings


class BaseModerator(ABC):
    def __init__(self, comment):
        self.comment = comment

    def is_accepted(self):
        raise NotImplementedError


class HiveModerator(BaseModerator):
    severity_threshold = 3  # Severity score at which text is flagged or moderated, configurable.
    restricted_classes = ['sexual', 'hate', 'violence', 'bullying', 'spam']  # Select classes to monitor

    def _get_hive_response(self):
        headers = {'Authorization': f'Token {settings.HIVE_MODERATION_API_KEY}'}
        data = {'text_data': self.comment.comment}  # Must be a string. This is also where you would insert metadata if desired.
        response = requests.post('https://api.thehive.ai/api/v2/task/sync', headers=headers, data=data)
        return response.json()

    def _handle_hive_classifications(self, response):
        # Create a dictionary where the classes are keys and the scores their respective values.
        is_accepted = True
        scores_dict = {x['class']: x['score'] for x in response['status'][0]['response']['output'][0]['classes']}
        for ea_class in self.restricted_classes:
            if scores_dict[ea_class] >= self.severity_threshold:
                is_accepted = False
                break

        return is_accepted

    def is_accepted(self):
        response = self._get_hive_response()
        return self._handle_hive_classifications(response)


class StubModerator(BaseModerator):
    def is_accepted(self):
        return True
