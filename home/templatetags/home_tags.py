from django import template
from home.models import Footer

register = template.Library()

@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def footer(context):
    return {
        'footer': Footer.objects.all()[0],
        'request': context['request'],
    }
