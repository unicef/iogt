import codecs
import cairosvg
import re

def convert_svg_to_png(svg_file, fill_color=None, stroke_color=None):
    with codecs.open(svg_file, encoding='utf-8', errors='ignore') as f:
        svg_file_text = f.read()
        png_file = svg_file.replace('svg', 'png')
        breakpoint()
        if fill_color:
            fill_match = re.findall(r"(fill\=\"(\w*|\W\w*)\")\/\>", svg_file_text)
            svg_file_text = svg_file_text.replace(fill_match[0][0], f'fill=\"{fill_color}\"')
        if stroke_color:
            stroke_match = re.findall(r"stroke=\"(\W\w+|\w*)\"", svg_file_text)
            svg_file_text = svg_file_text.replace(stroke_match[0], stroke_color)
        cairosvg.svg2png(bytestring=svg_file_text, write_to=png_file, scale=10.0)




convert_svg_to_png('../static/icons/back.svg', 'red')