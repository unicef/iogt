from rest_framework import pagination


class IoGTPagination(pagination.PageNumberPagination):
    page_size = 15
    max_page_size = 100
    page_size_query_param = 'page_size'
