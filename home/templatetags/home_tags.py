from django import template
import home.models as model

register = template.Library()

@register.inclusion_tag('home/tags/footer.html', takes_context=True)
def footer(context):
    return {
        'footer': model.Footer.objects.first(),
        'request': context['request'],
    }


@register.inclusion_tag('home/tags/articles_list.html')
def render_articles_list(articles):
    live_articles = articles.filter(live=True)
    return {'articles': live_articles}
