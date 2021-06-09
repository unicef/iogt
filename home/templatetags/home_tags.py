from django import template
from home.models import FooterPage

register = template.Library()


@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def footer(context):
    return {
        'footer_pages': FooterPage.objects.live(),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/articles_list.html')
def render_articles_list(articles):
    return {'articles': articles}


@register.inclusion_tag('home/tags/featured_content_list.html')
def render_featured_content_list(featured_content):
    return {'featured_content_items': featured_content}


@register.inclusion_tag('home/tags/banners_list.html')
def render_banners_list(banners):
    return {'banners': banners}
