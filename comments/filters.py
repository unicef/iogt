from django.contrib.admin import SimpleListFilter
from django.db.models import Count


class FlaggedFilter(SimpleListFilter):
    title = "Flagged?"
    parameter_name = "flagged"

    def lookups(self, request, model_admin):
        return [
            (True, 'Yes'),
            (False, 'No')
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.annotate(num_flags=Count('flags')).filter(num_flags__gt=0)
        return queryset
