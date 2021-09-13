from django import template

register = template.Library()


@register.simple_tag
def user_can_report(comment, user):
    if user.is_anonymous:
        return False
    return (comment.user != user) and not comment.flags.filter(user=user).exists()

@register.simple_tag
def filter_removed_comments(comments):
    return [comment for comment in comments if not comment['comment'].is_removed]

