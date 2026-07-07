from django import template
from sbc.models import SBCHeader
from sbc.models import SBCFooter

register = template.Library()


### Header
@register.inclusion_tag('sbc/components/header.html', takes_context=True)
def sbc_header(context):
    return {
        'header': SBCHeader.objects.first(),
        'request': context.get('request'),
    }


### Footer
@register.inclusion_tag('sbc/components/footer.html', takes_context=True)
def sbc_footer(context):
    return {
        'footer': SBCFooter.objects.first(),
        'request': context.get('request'),
    }
