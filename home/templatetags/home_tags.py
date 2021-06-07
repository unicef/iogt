from django import template
from home.models import FooterPage

register = template.Library()


@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def footer(context):
    return {
        'footer': FooterPage.objects.first(),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/articles_list.html')
def render_articles_list(articles):
    return {'articles': articles}
