from django.core.paginator import EmptyPage, Paginator
from django.template.response import TemplateResponse
from wagtail.models import Locale

from home.models import Article, Section
from iogt.settings.base import SEARCH_RESULTS_PER_PAGE
# from wagtail.search.models import Query
from questionnaires.models import Poll, Quiz, Survey


def search(request):
    search_groups = (Article, Poll, Quiz, Section, Survey)

    search_query = request.GET.get("query")
    page = int(request.GET.get("page", 1))

    results = {"search_query": search_query, "search_groups": {}}

    # Search
    sandbox_section = Section.objects.filter(slug='sandbox').first()
    sandbox_page_ids = []
    if sandbox_section:
        sandbox_page_ids = sandbox_section.get_descendants(inclusive=True).values_list('id', flat=True)

    for search_group in search_groups:
        search_results_count = 0
        if search_query:
            search_results = search_group.objects.exclude(id__in=sandbox_page_ids).live().\
                filter(locale=Locale.objects.get(language_code=request.LANGUAGE_CODE)).specific().search(search_query)
            search_results_count = search_results.count()
            # Removed in Wagtail 6+: Query.add_hit() was used to log search query usage statistics in the admin.
            # As of Wagtail 6 and later, this feature has been deprecated and the model `wagtail.search.models.Query` is no longer available.
            # If analytics are still desired, consider implementing a custom `SearchAnalytics` model to log queries,
            # or integrate with a third-party analytics platform like Google Analytics or Matomo.
            # Example: log query, timestamp, and whether results were found for later analysis.
            # query = Query.get(search_query)

            # # Record hit
            # query.add_hit()
        else:
            search_results = search_group.objects.none()

        # Pagination
        paginator = Paginator(search_results, SEARCH_RESULTS_PER_PAGE)
        try:
            search_results = paginator.page(page)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)

        if search_results:
            results["search_groups"][search_group._meta.verbose_name_plural] = {
                "search_results": search_results,
                "search_results_count": search_results_count,
            }

    return TemplateResponse(request, "search/search.html", results)
