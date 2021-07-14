import os

from django.core.files import File
from django.core.management.base import BaseCommand
from wagtailsvg.models import Svg


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--svg-dir',
            required=True,
            help='Path to IoGT SVG directory'
        )
        parser.add_argument(
            '--clean',
            required=False,
            action='store_true',
            help='Remove existing SVG'
        )

    def handle(self, *args, **options):
        self.svg_dir = options.get('svg_dir')
        clean = options.get('clean')
        if clean:
            self._clean()
        self._load_svg()

        self.stdout.write(self.style.SUCCESS('SVG loaded successfully.'))

    def _clean(self):
        Svg.objects.all().delete()
        self.stdout.write(self.style.ERROR('Existing SVG removed.'))

    def _open_svg_file(self, svg_path):
        try:
            return open(svg_path, 'rb')
        except:
            self.stdout.write(self.style.WARNING(f'SVG file not found: {svg_path}.'))

    def _load_svg(self):
        for dir in os.listdir(self.svg_dir):
            dir_path = os.path.join(self.svg_dir, dir)
            if os.path.isdir(dir_path):
                for svg_file in os.listdir(dir_path):
                    svg_path = os.path.join(dir_path, svg_file)
                    file = self._open_svg_file(svg_path)
                    if file:
                        svg = Svg.objects.create(title=svg_file.strip('.svg'), file=File(file, name=svg_file))
                        svg.tags.add(dir)
