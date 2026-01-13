from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from iogt_users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(first_name=None).update(first_name='')
        User.objects.filter(last_name=None).update(last_name='')
        self.stdout.write(_('Users have been saved successfully!'))
