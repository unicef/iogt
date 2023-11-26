from django.db import models
from iogt_users.models import User


class MoyaPayPayment(models.Model):
    amount = models.IntegerField()
    is_successful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.moyapay_username
