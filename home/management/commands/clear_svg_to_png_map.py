from django.core.management.base import BaseCommand

from home.models import SVGToPNGMap


class Command(BaseCommand):
    def handle(self, *args, **options):
        for map in SVGToPNGMap.objects.all():
            map.delete()
            map.png_image_file.delete()

        self.stdout.write(self.style.SUCCESS('SVG to PNG map cleared.'))
