from django import template
from home.models import Footer

register = template.Library()

@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def footer(context):
    return {
        'footer': Footer.objects.first(),
        'request': context['request'],
    }
