from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from home.models import Article, Section
from iogt.settings.base import SEARCH_RESULTS_PER_PAGE
from wagtail.search.models import Query
from django.core.exceptions import FieldDoesNotExist
from questionnaires.models import Poll, Quiz, Survey


def search(request):
    search_groups = (Article, Poll, Quiz, Section, Survey)

    search_query = request.GET.get("query")
    page = int(request.GET.get("page", 1))

    results = {"search_query": search_query, "search_groups": {}}

    # Search
    for search_group in search_groups:
        search_results_count = 0
        if search_query:
            search_results = search_group.objects.live().search(search_query)
            search_results_count = search_results.count()
            query = Query.get(search_query)

            # Record hit
            query.add_hit()
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
