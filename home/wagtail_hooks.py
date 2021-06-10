from urllib.parse import urlparse

from django.urls import resolve
from wagtail.core import hooks
from wagtail.core.models import Page


@hooks.register('construct_page_chooser_queryset')
def limit_page_chooser(pages, request):
    # TODO: add section check otherwise page chooser will break in other places like banner etc.
    current_url_match = resolve(urlparse(request.path)[2])
    if current_url_match.kwargs:
        page_id = current_url_match.kwargs.get('parent_page_id')
    else:
        referer_url_match = resolve(urlparse(request.META.get('HTTP_REFERER'))[2])
        page_id = referer_url_match.kwargs.get('page_id')

    return Page.objects.get(id=page_id).get_children()
