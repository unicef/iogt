from django.core.management.base import BaseCommand

from home.models import SVGToPNGMap


class Command(BaseCommand):
    def handle(self, *args, **options):
        SVGToPNGMap.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('SVG to PNG map cleared.'))
