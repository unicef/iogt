from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.response import TemplateResponse
from home.models import Article, Section
from iogt.settings.base import SEARCH_RESULTS_PER_PAGE
from wagtail.search.models import Query


def search(request):
    search_groups = (Article, Section)  # add models which should be searchable

    search_query = request.GET.get("query")
    page = request.GET.get("page", 1)

    results = {"search_query": search_query, "search_groups": {}}

    # Search
    for search_group in search_groups:
        search_results_no = 0
        if search_query:
            search_results = search_group.objects.live().search(search_query)
            search_results_no = search_results.count()
            query = Query.get(search_query)

            # Record hit
            query.add_hit()
        else:
            search_results = search_group.objects.none()

        # Pagination
        paginator = Paginator(search_results, SEARCH_RESULTS_PER_PAGE)
        try:
            search_results = paginator.page(page)
        except PageNotAnInteger:
            search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)

        if search_results:
            results["search_groups"][search_group.__name__] = {
                "search_results": search_results,
                "search_results_no": search_results_no,
            }

    return TemplateResponse(request, "search/search.html", results)
