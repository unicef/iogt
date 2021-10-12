from django import template
from django.conf import settings

from home.models import SVGToPNGMap

register = template.Library()


@register.inclusion_tag('home/tags/render_png.html')
def render_png_from_svg(svg_relative_path, height=None, width=None, fill_color=None, stroke_color=None, attrs=None):
    absolute_path = f'{settings.BASE_DIR}{svg_relative_path}'
    return {
        'image_url': SVGToPNGMap.get_png_image(absolute_path, fill_color=fill_color, stroke_color=stroke_color).url,
        'height': height,
        'width': width,
        'attrs': attrs,
    }

@register.simple_tag
def svg_to_png_url(svg_relative_path, fill_color=None, stroke_color=None,):
    absolute_path = f'{settings.BASE_DIR}{svg_relative_path}'
    return SVGToPNGMap.get_png_image(absolute_path, fill_color=fill_color, stroke_color=stroke_color).url