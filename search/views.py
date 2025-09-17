from django.core.paginator import EmptyPage, Paginator
from django.template.response import TemplateResponse
from wagtail.models import Locale, Page
from wagtail.contrib.search_promotions.models import Query, SearchPromotion

from home.models import Article, Section
from iogt.settings.base import SEARCH_RESULTS_PER_PAGE
from questionnaires.models import Poll, Quiz, Survey


def search(request):
    search_groups = (Article, Poll, Quiz, Section, Survey)
    search_query = request.GET.get("query")
    page = int(request.GET.get("page", 1))
    suggestions = []
    search_promotions = []
    if search_query:
        query = Query.get(search_query)
        # Record hit
        query.add_hit()
        search_promotions = SearchPromotion.objects.filter(query=query)
        suggestions = (
            Page.objects.live()
            .filter(title__icontains=search_query)
            .values_list("title", flat=True)[:5]
        )
    results = {
        "search_query": search_query,
        "search_groups": {},
        "suggested_queries": suggestions,
        "search_promotions": search_promotions,
    }
    sandbox_section = Section.objects.filter(slug="sandbox").first()
    sandbox_page_ids = []
    if sandbox_section:
        sandbox_page_ids = sandbox_section.get_descendants(inclusive=True).values_list("id", flat=True)
   
    for search_group in search_groups:
        if search_query:
            search_results = search_group.objects.exclude(id__in=sandbox_page_ids).live().\
                filter(locale=Locale.objects.get(language_code=request.LANGUAGE_CODE)).specific().search(search_query)
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
                "search_results_count": search_results.paginator.count,
            }

    return TemplateResponse(request, "search/search.html", results)
