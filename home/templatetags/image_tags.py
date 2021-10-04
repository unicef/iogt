from django import template
from django.conf import settings

from home.models import SVGToPNGMap

register = template.Library()


@register.inclusion_tag('home/tags/render_png.html')
def render_png_from_svg(svg_relative_path, fill_color):
    absolute_path = f'{settings.MEDIA_ROOT}{svg_relative_path}'
    return {
        'image_url' : SVGToPNGMap.get_png_image(absolute_path, color=fill_color)
    }
