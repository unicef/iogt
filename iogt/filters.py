from django_filters import rest_framework as filters


class ListIdFilter(filters.Filter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_expr = 'in'

    def filter(self, queryset, value):
        list_values = value.split(',') if value else []
        return super().filter(queryset, list_values)
