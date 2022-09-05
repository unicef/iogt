from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, ListView
from django_comments.views.comments import post_comment
from django_comments_xtd.models import XtdComment
from django.utils.translation import ugettext as _

from comments.forms import AdminCommentForm, CommentFilterForm
from comments.models import CannedResponse


def update(request, comment_pk, action):
    get_comment_with_children_filter = Q(parent_id=comment_pk) | Q(pk=comment_pk)
    comments = XtdComment.objects.filter(get_comment_with_children_filter)
    verb = ''
    if action == 'unpublish':
        for comment in comments:
            comment.is_public = False
        verb = 'unpublished'
    elif action == 'publish':
        for comment in comments:
            comment.is_public = True
            comment.comment_moderation.is_valid = True
            comment.comment_moderation.save(update_fields=['is_valid'])
        verb = 'published'
    elif action == 'hide':
        for comment in comments:
            comment.is_removed = True
        verb = 'removed'
    elif action == 'show':
        for comment in comments:
            comment.is_removed = False
        verb = 'shown'
    elif action == 'clear_flags':
        comment = XtdComment.objects.get(pk=comment_pk)
        comment.flags.all().delete()
        verb = 'cleared'
    elif action == 'manual_validated':
        for comment in comments:
            comment.comment_moderation.is_manual_validated = True
            comment.comment_moderation.manual_validated_by = request.user
            comment.comment_moderation.save(update_fields=['is_manual_validated', 'manual_validated_by'])
        verb = 'validated'
    XtdComment.objects.bulk_update(comments, ['is_public', 'is_removed'])

    messages.success(request, _(f'The comment has been {verb} successfully!'))

    return redirect(request.META.get('HTTP_REFERER'))


class CommentReplyView(TemplateView):
    template_name = 'comment_reply.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = XtdComment.objects.get(pk=kwargs['comment_pk'])
        context.update({
            'form': AdminCommentForm(comment.content_object, comment=comment),
            'comment': comment,
            'canned_responses': CannedResponse.objects.all()
        })
        return context


@csrf_protect
@require_POST
def post_admin_comment(request):
    """
    This is a hack to make the post comment view send a message. There
    was no better way to do this than use a decorator pattern. Suggestions/Improvements
    are welcome
    :param request:
    :return:
    """
    response = post_comment(request, next='/')
    messages.success(request, _("Sent Reply successfully"))
    return response


class ProcessCannedResponseView(View):
    def post(self, request):
        referer = request.META.get('HTTP_REFERER')
        canned_response_id = request.POST.get('canned_responses')
        parsed_url = urlparse(referer)

        if not request.user.has_perm('django_comments_xtd.can_moderate'):
            messages.error(request, _("You do not have the permission to perform this action."))
        else:
            query_dict = dict(parse_qsl(parsed_url.query))
            canned_response_text = get_object_or_404(CannedResponse,
                                                     pk=canned_response_id).text if canned_response_id else ''
            comment_text = request.POST.get('comment')
            query_dict.update({'canned_response': f'{comment_text} {canned_response_text}'})

            parsed_url = parsed_url._replace(query=urlencode(query_dict))

        referer_url = urlunparse(parsed_url)
        return redirect(to=referer_url)


class CommentsModerationView(ListView):
    model = XtdComment
    template_name = 'comments/moderation.html'
    context_object_name = 'comments'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.has_perm('django_comments_xtd.can_moderate') or settings.ENABLE_FE_COMMENTS_MODERATION):
            raise PermissionDenied(
                "You do not have permission."
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            comment_moderation__is_manual_validated=False).annotate(num_flags=Count('flags'))
        form = CommentFilterForm(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data
            is_valid = data['is_valid']
            is_flagged = data['is_flagged']
            is_removed = data['is_removed']
            is_public = data['is_public']
            from_date = data['from_date']
            to_date = data['to_date']

            if is_valid != '':
                queryset = queryset.filter(comment_moderation__is_valid=is_valid)
            if is_flagged != '':
                if is_flagged:
                    queryset = queryset.filter(num_flags__gt=0)
                else:
                    queryset = queryset.filter(num_flags=0)
            if is_removed != '':
                queryset = queryset.filter(is_removed=is_removed)
            if is_public != '':
                queryset = queryset.filter(is_public=is_public)
            if to_date:
                if from_date:
                    queryset = queryset.filter(submit_date__date__range=[from_date, to_date])
                else:
                    queryset = queryset.filter(submit_date__date__lte=to_date)
            elif from_date:
                queryset = queryset.filter(submit_date__date__gte=from_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = CommentFilterForm(self.request.GET)
        if form.is_valid():
            data = form.cleaned_data
            context.update({
                'form': form,
                'params': urlencode(data)
            })
        return context
