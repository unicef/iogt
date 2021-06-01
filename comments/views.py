from django.urls import reverse
from django.contrib import messages
from wagtail.core.models import Page
from django.shortcuts import redirect, render
from django_comments_xtd.models import XtdComment
from django.utils.translation import ugettext as _
from .utils import cleaned_tree


def pages(request):
    comments = XtdComment.objects.all()
    pages = []
    for comment in comments:
        page_model = comment.content_type.model_class()
        page_id = comment.object_pk
        try:
            page = page_model.objects.get(pk=page_id)
            if not any(d['pk'] == page_id and d['model'] == page for d in pages):
                pages.append({
                    'pk': page_id,
                    'model': page})
        except:
            pass
    return render(request, 'wagtail_comments_xtd/pages.html', {
        'pages': pages,
    })


def comments(request, pk):
    page = Page.objects.get(pk=pk)
    comments = XtdComment.objects.filter(object_pk=pk, level=False)

    return render(request, 'wagtail_comments_xtd/comments.html', {
        'page': page,
        'comments': cleaned_tree(comments),
    })


def comment_thread(request, page_pk, comment_pk):
    page = Page.objects.get(pk=page_pk)
    comments = XtdComment.objects.filter(parent_id=comment_pk).exclude(pk=comment_pk)

    return render(request, 'wagtail_comments_xtd/comments.html', {
        'page': page,
        'comment': XtdComment.objects.get(pk=comment_pk),
        'comments': cleaned_tree(comments),
    })


def update(request, page_pk, comment_pk, action):

    # Fetch the current comment and all child comments.
    # If we perform an action on just the parent, django_commnents_xtd's tree_from_queryset
    # query fails to correctly return comments suitable for output.
    # https://github.com/danirus/django-comments-xtd/blob/323cb394147120a5cacb9771ab527783b232132a/django_comments_xtd/models.py#L121
    comments = XtdComment.objects.filter(parent_id=comment_pk)

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
    XtdComment.objects.bulk_update(comments, ['is_public', 'is_removed'])

    messages.success(request, _("The comment has been updated successfully!"))

    return redirect(request.META.get('HTTP_REFERER'))
