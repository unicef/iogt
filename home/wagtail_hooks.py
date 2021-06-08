from wagtail.core import hooks

from home.models import FooterIndexPage


@hooks.register('construct_explorer_page_queryset')
def sort_footer_page_listing_by_path(parent_page, pages, request):
    if isinstance(parent_page, FooterIndexPage):
        pages = pages.order_by('path')

    return pages
