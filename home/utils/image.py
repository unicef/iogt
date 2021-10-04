import codecs
import cairosvg
import re

from django.core.files.base import ContentFile


def convert_svg_to_png_bytes(svg_file, fill_color=None, stroke_color=None, scale=100):
    with codecs.open(svg_file, encoding='utf-8', errors='ignore') as f:
        svg_file_text = f.read()
        if fill_color:
            fill_match = re.findall(r"(fill=\".*?\")", svg_file_text)
            # doing this because parent tag "svg" also has a fill attribute but we replace only
            # child tag "path" fill attribute
            if len(fill_match) == 2:
                svg_file_text = svg_file_text.replace(fill_match[1], f"fill=\"{fill_color}\"")

        if stroke_color:
            stroke_match = re.findall(r"(stroke=\".*?\")", svg_file_text)
            try:
                svg_file_text = svg_file_text.replace(stroke_match[0], f"stroke=\"{stroke_color}\"")
            except IndexError:
                pass

    file_bytes = cairosvg.svg2png(bytestring=svg_file_text, scale=scale)
    return ContentFile(file_bytes, 'test.png')