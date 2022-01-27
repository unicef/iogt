from django import template
from django_comments_xtd.models import LIKEDIT_FLAG, DISLIKEDIT_FLAG

register = template.Library()


@register.simple_tag
def user_can_report(comment, user):
    if user.is_anonymous:
        return False
    return (comment.user != user) and not comment.flags.filter(user=user).exists()


@register.simple_tag
def filter_removed_comments(comments):
    return [comment for comment in comments if not comment['comment'].is_removed]


@register.simple_tag
def get_comments_page(comments, request):
    return list(reversed(comments))[:get_current_num_records(request)]


@register.simple_tag
def has_more_comments(comments, request):
    return get_current_num_records(request) < len(comments)


@register.simple_tag
def get_current_num_records(request):
    return int(request.GET.get('num_records', 5))


@register.simple_tag
def get_next_num_records(request):
    current_num_records = int(request.GET.get('num_records', 5))
    return current_num_records + 5


@register.simple_tag
def get_comment_report_count(comment):
    return comment.flags.exclude(flag__in=[LIKEDIT_FLAG, DISLIKEDIT_FLAG]).count()
