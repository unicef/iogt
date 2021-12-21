import logging
from pathlib import Path
from django import template
from django.conf import settings

from home.models import SVGToPNGMap

register = template.Library()
logger = logging.getLogger(__name__)


@register.inclusion_tag('home/tags/render_png.html')
def render_png_from_svg(svg_relative_path, icon=None, height=None, width=None, fill_color=None, stroke_color=None, attrs=None):
    try:
        if icon:
            svg_relative_path = f"media/{icon.file}"
        return {
            'image_url': svg_to_png_url(svg_relative_path, fill_color=fill_color, stroke_color=stroke_color),
            'height': height,
            'width': width,
            'attrs': attrs,
        }
    except:
        return {}

@register.simple_tag
def svg_to_png_url(svg_relative_path, fill_color=None, stroke_color=None,):
    absolute_path = Path(settings.BASE_DIR) / svg_relative_path
    try:
        return SVGToPNGMap.get_png_image(absolute_path, fill_color=fill_color, stroke_color=stroke_color).url
    except:
        message = f"Failed to convert SVG to PNG, file={absolute_path}"
        logger.warning(message)
        raise Error(message)
