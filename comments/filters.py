from django.contrib.admin import SimpleListFilter
from django.db.models import Count

from comments.models import CommentModeration


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


class StatusFilter(SimpleListFilter):
    title = "Status?"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [
            (CommentModeration.CommentModerationStatus.UNMODERATED, 'Unmoderated'),
            (CommentModeration.CommentModerationStatus.PUBLISHED, 'Published'),
            (CommentModeration.CommentModerationStatus.UNPUBLISHED, 'Unpublished'),
            (CommentModeration.CommentModerationStatus.UNSURE, 'Unsure'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(comment_moderation__status=self.value())
        return queryset
