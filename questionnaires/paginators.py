from rest_framework import pagination


class IoGTPagination(pagination.PageNumberPagination):
    page_size = None
    max_page_size = 10
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        self.page_size = request.query_params.get(self.page_size_query_param) or queryset.count()
        return super().paginate_queryset(queryset, request, view)
