from abc import ABC

from django.conf import settings


class BaseModerator(ABC):
    @classmethod
    def moderate(cls, comment):
        raise NotImplementedError


class BlacklistedWordsModerator(BaseModerator):
    @classmethod
    def moderate(cls, comment):
        for blacklisted_word in settings.BLACKLISTED_WORDS:
            if blacklisted_word in comment.comment:
                return False

        return True


class AlwaysApproveModerator(BaseModerator):
    @classmethod
    def moderate(cls, comment):
        return True
