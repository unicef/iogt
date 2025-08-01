from django import template
from bs4 import BeautifulSoup

register = template.Library()

@register.filter
def strip_html(value):
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text(separator=" ", strip=True)
