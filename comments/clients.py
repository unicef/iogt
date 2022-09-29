from abc import ABC

from django.conf import settings


class BaseModerator(ABC):
    @classmethod
    def is_valid(cls, comment):
        raise NotImplementedError


class BlacklistedWordsModerator(BaseModerator):
    @classmethod
    def is_valid(cls, comment):
        for blacklisted_word in settings.BLACKLISTED_WORDS:
            if blacklisted_word in comment.comment:
                return False

        return True
