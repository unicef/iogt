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
from django.contrib.auth.decorators import permission_required

from comments.forms import AdminCommentForm, CommentFilterForm
from comments.models import CannedResponse, CommunityCommentModeration


@permission_required('comments.can_moderate_on_public_site')
def update(request, comment_pk, action):
    get_comment_with_children_filter = Q(parent_id=comment_pk) | Q(pk=comment_pk)
    comments = XtdComment.objects.filter(get_comment_with_children_filter)
    comment_moderations = []
    verb = ''
    if action == 'approve':
        for comment in comments:
            comment.is_public = True
            comment.flags.all().delete()
            comment_moderation = comment.comment_moderation
            comment_moderation.state = CommunityCommentModeration.State.APPROVED
            comment_moderations.append(comment_moderation)
        verb = 'approved'
    elif action == 'reject':
        for comment in comments:
            comment.is_public = False
            comment_moderation = comment.comment_moderation
            comment_moderation.state = CommunityCommentModeration.State.REJECTED
            comment_moderations.append(comment_moderation)
        verb = 'rejected'
    elif action == 'unsure':
        for comment in comments:
            comment_moderation = comment.comment_moderation
            comment_moderation.state = CommunityCommentModeration.State.UNSURE
            comment_moderations.append(comment_moderation)
        verb = 'unsure'
    elif action == 'unpublish':
        for comment in comments:
            comment.is_public = False
        verb = 'unpublished'
    elif action == 'publish':
        for comment in comments:
            comment.is_public = True
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
    XtdComment.objects.bulk_update(comments, ['is_public', 'is_removed'])
    CommunityCommentModeration.objects.bulk_update(comment_moderations, ['state'])

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

        if not request.user.has_perm('comments.can_moderate_on_public_site'):
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


class CommentsCommunityModerationView(ListView):
    model = XtdComment
    template_name = 'comments/community_moderation.html'
    context_object_name = 'comments'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not settings.COMMENTS_COMMUNITY_MODERATION or not request.user.has_perm('comments.can_moderate_on_public_site'):
            raise PermissionDenied(
                "You do not have permission."
            )
        return super().dispatch(request, *args, **kwargs)

    def _get_form(self):
        return CommentFilterForm(self.request.GET or {'state': CommunityCommentModeration.State.UNMODERATED})

    def get_queryset(self):
        queryset = super().get_queryset().filter(comment_moderation__isnull=False).order_by('-submit_date')
        form = self._get_form()
        if form.is_valid():
            data = form.cleaned_data
            state = data['state']
            from_date = data['from_date']
            to_date = data['to_date']

            if state != 'ALL':
                queryset = queryset.filter(comment_moderation__state=state)

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
        form = self._get_form()
        if form.is_valid():
            data = form.cleaned_data
            context.update({
                'form': form,
                'params': urlencode(data)
            })
        return context
