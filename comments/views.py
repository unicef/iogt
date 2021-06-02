from django.db.models import Q
from django.contrib import messages
from django.shortcuts import redirect
from django_comments_xtd.models import XtdComment
from django.utils.translation import ugettext as _


def update(request, comment_pk, action):
    get_comment_with_children_filter = Q(parent_id=comment_pk) | Q(pk=comment_pk)
    comments = XtdComment.objects.filter(get_comment_with_children_filter)

    if action == 'unpublish':
        for comment in comments:
            comment.is_public = False
    elif action == 'publish':
        for comment in comments:
            comment.is_public = True
    elif action == 'hide':
        for comment in comments:
            comment.is_removed = True
    elif action == 'show':
        for comment in comments:
            comment.is_removed = False
    elif action == 'clear_flags':
        for comment in comments:
            comment.flags.all().delete()
    XtdComment.objects.bulk_update(comments, ['is_public', 'is_removed'])

    messages.success(request, _("The comment has been updated successfully!"))

    return redirect(request.META.get('HTTP_REFERER'))
