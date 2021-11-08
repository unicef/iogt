import codecs
import cairosvg
import re

from bs4 import BeautifulSoup
from django.core.files.base import ContentFile


def convert_svg_to_png_bytes(svg_file_path, fill_color=None, stroke_color=None, scale=100):
    with open(svg_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')
        elements_to_fill = soup.find_all('path')
        for el in elements_to_fill:
            if fill_color:
                el['fill'] = fill_color
            if stroke_color:
                el['stroke'] = stroke_color

    parsed_soup = str(soup.body.next)
    parsed_soup = parsed_soup.replace('viewbox', 'viewBox')

    file_bytes = cairosvg.svg2png(bytestring=parsed_soup, scale=scale)
    return ContentFile(file_bytes, 'svg-to-png.png')