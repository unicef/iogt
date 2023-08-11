from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q
from django_comments.models import CommentFlag

from comments.models import CommentModerationState


class FlaggedFilter(SimpleListFilter):
    title = "flagged for removal"
    parameter_name = "flagged"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        qs = queryset.annotate(
            num_flags=Count("flags", Q(flags__flag=CommentFlag.SUGGEST_REMOVAL))
        )

        if self.value() == "yes":
            return qs.filter(num_flags__gt=0)

        if self.value() == "no":
            return qs.filter(num_flags__lt=1)


class PublishedFilter(SimpleListFilter):
    title = "published"
    parameter_name = "is_published"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(is_public=True if self.value() == "yes" else False)


class ModerationFilter(SimpleListFilter):
    title = "moderation status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return CommentModerationState.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(comment_moderation__state=self.value())
