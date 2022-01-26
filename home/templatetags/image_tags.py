from django import template
from django.conf import settings

from home.models import SVGToPNGMap

register = template.Library()


@register.simple_tag
def svg_to_png_url(svg_relative_path, fill_color=None, stroke_color=None,):
    absolute_path = f'{settings.BASE_DIR}{svg_relative_path}'
    return SVGToPNGMap.get_png_image(absolute_path, fill_color=fill_color, stroke_color=stroke_color).url


@register.inclusion_tag('home/tags/render_png.html')
def render_icon(icon_path=None, icon=None, height=None, width=None, fill_color=None, stroke_color=None, attrs=None):
    image_url = ''
    if icon_path or (icon and icon.is_svg_icon):
        svg_path = icon_path or icon.url
        image_url = svg_to_png_url(svg_relative_path=svg_path, fill_color=fill_color, stroke_color=stroke_color)
    elif icon:
        image_url = icon.url

    return {
        'height': height,
        'width': width,
        'attrs': attrs,
        'image_url': image_url,
    }
