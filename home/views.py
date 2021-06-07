from django.http import HttpResponseRedirect
from wagtail.admin.views.pages.listing import index as wagtailadmin_explore

from home.models import FooterIndexPage


def override_wagtailadmin_explore_default_ordering(request, parent_page_id):
    """
    Wrap Wagtail's explore view to change the default ordering
    """
    if request.method == 'GET' and 'ordering' not in request.GET:
        # Display reordering handles by default for children of FooterIndexPage type.
        if FooterIndexPage.objects.filter(id=parent_page_id).first():
            return HttpResponseRedirect(request.path_info + '?ordering=ord')

    return wagtailadmin_explore(request, parent_page_id=parent_page_id)
