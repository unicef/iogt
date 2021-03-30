from django import template
from home.models import Footer
import datetime
import json

register = template.Library()

@register.simple_tag(takes_context=True)
def dump_context(context: template.RequestContext):
    return context.request

@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def footer(context):
    return {
        'footer': Footer.objects.first(),
        'request': context['request'],
    }
