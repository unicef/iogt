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


class ModerationFilter(SimpleListFilter):
    title = "Moderation?"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [
            (CommentModeration.CommentModerationState.UNMODERATED, 'Unmoderated'),
            (CommentModeration.CommentModerationState.APPROVED, 'Approved'),
            (CommentModeration.CommentModerationState.REJECTED, 'Rejected'),
            (CommentModeration.CommentModerationState.UNSURE, 'Unsure'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(comment_moderation__state=self.value())
        return queryset


class PublishedFilter(SimpleListFilter):
    title = "Published?"
    parameter_name = "is_published"

    def lookups(self, request, model_admin):
        return [
            (True, 'Yes'),
            (False, 'No')
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(is_public=self.value())
        return queryset
