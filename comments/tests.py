from django.test import TestCase
from django.urls import reverse
from iogt_users.factories import UserFactory

from comments.factories import (
    AdminModeratorFactory,
    CommentFactory,
    CommunityModeratorFactory,
    FlagFactory,
)
from comments.models import CommentModerationState as State


class CommentModerationTest(TestCase):
    def setUp(self):
        self.user = UserFactory(first_name="Unprivileged", last_name="User")
        self.admin_moderator = AdminModeratorFactory()
        self.community_moderator = CommunityModeratorFactory()

    def test_community_moderator_can_approve(self):
        self.comment = CommentFactory(is_public=False)
        FlagFactory(comment=self.comment, user=self.user)
        self.assertEqual(self.comment.flags.count(), 1)
        self.assertAuthorized(self.community_moderator, "approve")
        self.assertTrue(self.comment.is_public)
        self.assertEqual(self.comment.flags.count(), 1, "Flags should remain")
        self.assertEqual(self.comment.comment_moderation.state, State.APPROVED)

    def test_community_moderator_can_reject(self):
        self.comment = CommentFactory(is_public=True)
        self.assertAuthorized(self.community_moderator, "reject")
        self.assertFalse(self.comment.is_public)
        self.assertEqual(self.comment.comment_moderation.state, State.REJECTED)

    def test_community_moderator_can_mark_unsure(self):
        self.comment = CommentFactory()
        self.assertAuthorized(self.community_moderator, "unsure")
        self.assertEqual(self.comment.comment_moderation.state, State.UNSURE)

    def test_community_moderator_can_hide(self):
        self.comment = CommentFactory(is_removed=False)
        self.assertAuthorized(self.community_moderator, "hide")
        self.assertTrue(self.comment.is_removed)

    def test_admin_moderator_can_publish(self):
        self.comment = CommentFactory(is_public=False)
        self.assertAuthorized(self.admin_moderator, "publish")
        self.assertTrue(self.comment.is_public)

    def test_admin_moderator_can_unpublish_comment(self):
        self.comment = CommentFactory(is_public=True)
        self.assertAuthorized(self.admin_moderator, "unpublish")
        self.assertFalse(self.comment.is_public)

    def test_admin_moderator_can_clear_flags_from_comment(self):
        self.comment = CommentFactory()
        FlagFactory(user=self.user, comment=self.comment)
        self.assertGreater(self.comment.flags.count(), 0)
        self.assertAuthorized(self.admin_moderator, "clear_flags")
        self.assertEqual(self.comment.flags.count(), 0)

    def test_community_moderator_cannot_perform_admin_moderator_actions(self):
        self.comment = CommentFactory()
        for action in ["publish", "unpublish", "clear_flags"]:
            self.assertUnauthorized(self.community_moderator, action)

    def test_admin_moderator_cannot_perform_community_moderator_actions(self):
        self.comment = CommentFactory()
        for action in ["approve", "reject", "unsure", "hide"]:
            self.assertUnauthorized(self.admin_moderator, action)

    def test_unprivileged_user_cannot_perform_any_action(self):
        self.comment = CommentFactory()
        for action in [
            "approve",
            "reject",
            "unsure",
            "hide",
            "publish",
            "unpublish",
            "clear_flags",
        ]:
            self.assertUnauthorized(self.user, action)

    def assertUnauthorized(self, user, action):
        self.assertEqual(
            self.performAction(user, action).status_code,
            403,
            f"'{user.first_name} {user.last_name}' should not be authorized to perform "
            f"'{action}' action",
        )

    def assertAuthorized(self, user, action):
        response = self.performAction(user, action)
        self.assertEqual(
            response.status_code,
            302,
            f"'{user.first_name} {user.last_name}' should be authorized to perform "
            f"'{action}' action",
        )
        self.assertEqual(
            response.url,
            "/referer/",
            "User should be redirected to referer URL",
        )
        self.comment.refresh_from_db()

    def performAction(self, user, action):
        self.client.force_login(user)
        return self.client.get(
            reverse(f"comment_{action}", args=[self.comment.id]),
            HTTP_REFERER="/referer/",
        )
        self.client.logout()
