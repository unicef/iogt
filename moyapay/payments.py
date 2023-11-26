from django.utils import timezone

from moyapay.client import MoyaPayClient
from moyapay.utils import can_process_payment


class MoyaPayModeratorPayout:
    def __init__(self, user, comment):
        self.user = user
        self.comment = comment
        self.amount = 50
        self.client = MoyaPayClient()
        self.client.authenticate()
        self.current_datetime = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    def process_payment(self):
        can_process_payment(self.user, self.comment)
