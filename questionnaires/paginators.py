from rest_framework import pagination


class IoGTPagination(pagination.PageNumberPagination):
    page_size = None
    max_page_size = 10
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = request.query_params.get(self.page_size_query_param) or queryset.count()
        return super().paginate_queryset(queryset, request, view)
