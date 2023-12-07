from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, TemplateView
from django_comments.views.comments import post_comment
from django_comments_xtd.models import XtdComment

from comments.forms import AdminCommentForm, CommentFilterForm
from comments.models import (
    CannedResponse,
    CommentModerationState,
    CommunityCommentModeration,
)


class BaseCommentView(LoginRequiredMixin, PermissionRequiredMixin, View):
    action_verb = ""

    def get_queryset(self, comment_pk):
        return XtdComment.objects.filter(Q(parent_id=comment_pk) | Q(pk=comment_pk))

    def get(self, request, comment_pk):
        comments = [
            self.handle(comment)
            for comment in self.get_queryset(comment_pk)
        ]
        comment_moderations = [comment.comment_moderation for comment in comments]

        XtdComment.objects.bulk_update(comments, ["is_public", "is_removed"])
        CommunityCommentModeration.objects.bulk_update(comment_moderations, ["state"])

        messages.success(
            request, _(f"The comment has been {self.action_verb} successfully!")
        )

        return redirect(request.META.get("HTTP_REFERER"))

    def handle(self, comment):
        return comment


class ApproveCommentView(BaseCommentView):
    permission_required = "comments.can_community_moderate"
    action_verb = "approved"

    def handle(self, comment):
        comment.is_public = True
        comment.comment_moderation.state = CommentModerationState.APPROVED
        return comment


class RejectCommentView(BaseCommentView):
    permission_required = "comments.can_community_moderate"
    action_verb = "rejected"

    def handle(self, comment):
        comment.is_public = False
        comment.comment_moderation.state = CommentModerationState.REJECTED
        return comment


class UnsureCommentView(BaseCommentView):
    permission_required = "comments.can_community_moderate"
    action_verb = "unsure"

    def handle(self, comment):
        comment.comment_moderation.state = CommentModerationState.UNSURE
        return comment


class HideCommentView(BaseCommentView):
    permission_required = "comments.can_community_moderate"
    action_verb = "removed"

    def handle(self, comment):
        comment.is_removed = True
        return comment


class PublishCommentView(BaseCommentView):
    permission_required = "django_comments_xtd.can_moderate"
    action_verb = "published"

    def handle(self, comment):
        comment.is_public = True
        return comment


class UnpublishCommentView(BaseCommentView):
    permission_required = "django_comments_xtd.can_moderate"
    action_verb = "unpublished"

    def handle(self, comment):
        comment.is_public = False
        return comment


class ClearFlagsCommentView(BaseCommentView):
    permission_required = "django_comments_xtd.can_moderate"
    action_verb = "cleared"

    def get_queryset(self, comment_pk):
        return XtdComment.objects.filter(pk=comment_pk)

    def handle(self, comment):
        comment.flags.all().delete()
        return comment


class CommentReplyView(TemplateView):
    template_name = "comment_reply.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment = XtdComment.objects.get(pk=kwargs["comment_pk"])
        context.update(
            {
                "form": AdminCommentForm(comment.content_object, comment=comment),
                "comment": comment,
                "canned_responses": CannedResponse.objects.all(),
            }
        )
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
    response = post_comment(request, next="/")
    messages.success(request, _("Sent Reply successfully"))
    return response


class ProcessCannedResponseView(View):
    def post(self, request):
        referer = request.META.get("HTTP_REFERER")
        canned_response_id = request.POST.get("canned_responses")
        parsed_url = urlparse(referer)

        if not request.user.has_perm("comments.can_community_moderate"):
            messages.error(
                request, _("You do not have the permission to perform this action.")
            )
        else:
            query_dict = dict(parse_qsl(parsed_url.query))
            canned_response_text = (
                get_object_or_404(CannedResponse, pk=canned_response_id).text
                if canned_response_id
                else ""
            )
            comment_text = request.POST.get("comment")
            query_dict.update(
                {"canned_response": f"{comment_text} {canned_response_text}"}
            )

            parsed_url = parsed_url._replace(query=urlencode(query_dict))

        referer_url = urlunparse(parsed_url)
        return redirect(to=referer_url)


class CommentsCommunityModerationView(ListView):
    model = XtdComment
    template_name = "comments/community_moderation.html"
    context_object_name = "comments"
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not settings.COMMENTS_COMMUNITY_MODERATION or not request.user.has_perm(
            "comments.can_community_moderate"
        ):
            raise PermissionDenied("You do not have permission.")
        return super().dispatch(request, *args, **kwargs)

    def _get_form(self):
        return CommentFilterForm(
            self.request.GET or {"state": CommentModerationState.UNMODERATED}
        )

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .filter(comment_moderation__isnull=False)
            .order_by("-submit_date")
        )
        form = self._get_form()
        if form.is_valid():
            data = form.cleaned_data
            state = data["state"]
            from_date = data["from_date"]
            to_date = data["to_date"]

            if state != "ALL":
                queryset = queryset.filter(comment_moderation__state=state)

            if to_date:
                if from_date:
                    queryset = queryset.filter(
                        submit_date__date__range=[from_date, to_date]
                    )
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
            context.update({"form": form, "params": urlencode(data)})
        return context
