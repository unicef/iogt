from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory
from django.urls import reverse

from comments.factories import XtdCommentFactory, CommunityCommentModeratorFactory, AdminCommentModeratorFactory
from comments.views import ApproveCommentView, RejectCommentView, UnSureCommentView, HideCommentView, \
    PublishCommentView, UnPublishCommentView, ClearFlagsCommentView
from iogt_users.factories import UserFactory


class CommentModerationTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.admin_comment_moderator = AdminCommentModeratorFactory()
        self.community_comment_moderator = CommunityCommentModeratorFactory()
        self.comment = XtdCommentFactory()
        self.request = RequestFactory()

    def set_up_request(self, view, user, comment_action_url):
        request = self.request.get(reverse(comment_action_url, args=[self.comment.id]))
        request.user = user
        request.session = 'session'
        request._messages = FallbackStorage(request)
        request.META['HTTP_REFERER'] = request.path

        response = view(request, comment_pk=self.comment.id)

        return response

    def test_approve_comment_view_as_admin_comment_moderator(self):
        view = ApproveCommentView.as_view()

        request = self.request.get(reverse('comment_approve', args=[self.comment.id]))
        request.user = self.admin_comment_moderator

        with self.assertRaises(PermissionDenied):
            view(request, comment_pk=self.comment.id)

    def test_approve_comment_view_as_user(self):
        view = ApproveCommentView.as_view()

        request = self.request.get(reverse('comment_approve', args=[self.comment.id]))
        request.user = self.user

        with self.assertRaises(PermissionDenied):
            view(request, comment_pk=self.comment.id)

    def test_approve_comment_view_as_community_comment_moderator(self):
        view = ApproveCommentView.as_view()
        response = self.set_up_request(view, self.community_comment_moderator, 'comment_approve')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.comment.comment_moderation.state, 'APPROVED')

    def test_reject_comment_view_as_community_comment_moderator(self):
        view = RejectCommentView.as_view()
        response = self.set_up_request(view, self.community_comment_moderator, 'comment_reject')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.comment.comment_moderation.state, 'REJECTED')

    def test_unsure_comment_view_as_community_comment_moderator(self):
        view = UnSureCommentView.as_view()
        response = self.set_up_request(view, self.community_comment_moderator, 'comment_unsure')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.comment.comment_moderation.state, 'UNSURE')

    def test_hide_comment_view_as_community_comment_moderator(self):
        view = HideCommentView.as_view()
        response = self.set_up_request(view, self.community_comment_moderator, 'comment_hide')
        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.comment.is_removed)

    def test_publish_comment_view_as_admin_comment_moderator(self):
        view = PublishCommentView.as_view()

        self.comment.is_public = False
        response = self.set_up_request(view, self.admin_comment_moderator, 'comment_publish')
        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.comment.is_public)

    def test_unpublish_comment_view_as_admin_comment_moderator(self):
        view = UnPublishCommentView.as_view()
        response = self.set_up_request(view, self.admin_comment_moderator, 'comment_unpublish')
        self.comment.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.comment.is_public)

    def test_clear_flags_comment_view_as_admin_comment_moderator(self):
        view = ClearFlagsCommentView.as_view()
        response = self.set_up_request(view, self.admin_comment_moderator, 'comment_clear_flags')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.comment.flags.count(), 0)
