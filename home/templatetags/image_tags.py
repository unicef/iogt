from pathlib import Path
from django import template
from django.conf import settings

from home.models import SVGToPNGMap

register = template.Library()


@register.simple_tag
def svg_to_png_url(svg_path, fill_color=None, stroke_color=None,):
    image = SVGToPNGMap.get_png_image(svg_path, fill_color=fill_color, stroke_color=stroke_color)
    return image.url if image else ''


@register.inclusion_tag('home/tags/render_png.html')
def render_icon(icon_path=None, icon=None, height=None, width=None, fill_color=None, stroke_color=None, attrs=None):
    image_url = ''
    if icon_path:
        image_url = svg_to_png_url(
            svg_path=Path(settings.STATIC_ROOT) / icon_path,
            fill_color=fill_color,
            stroke_color=stroke_color
        )
    elif icon:
        if icon.is_svg_icon:
            image_url = svg_to_png_url(
                svg_path=Path(settings.MEDIA_ROOT) / icon.path,
                fill_color=fill_color,
                stroke_color=stroke_color
            )
        else:
            image_url = icon.url

    return {
        'height': height,
        'width': width,
        'attrs': attrs,
        'image_url': image_url,
    }
