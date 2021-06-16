from django.test import TestCase
from django.urls import reverse

from comments.wagtail_hooks import XtdCommentAdmin
from iogt_users.factories import UserFactory

from .factories import CommentFactory, CommentFlagFactory


class CommentUpdateTests(TestCase):
    def setUp(self):
        self.user = UserFactory(is_superuser=True)
        self.client.force_login(self.user)

    def test_publish_comment(self):
        comment = CommentFactory(user=self.user, is_public=False)
        self.assertFalse(comment.is_public)

        url = reverse('wagtail_comments_xtd_publication', kwargs={'comment_pk': comment.id, 'action': 'publish'})
        response = self.client.get(url, HTTP_REFERER=XtdCommentAdmin().url_helper.get_action_url('index'))

        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertTrue(comment.is_public)

    def test_unpublish_comment(self):
        comment = CommentFactory(user=self.user, is_public=True)
        self.assertTrue(comment.is_public)

        url = reverse('wagtail_comments_xtd_publication', kwargs={'comment_pk': comment.id, 'action': 'unpublish'})
        response = self.client.get(url, HTTP_REFERER=XtdCommentAdmin().url_helper.get_action_url('index'))

        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertFalse(comment.is_public)

    def test_show_comment(self):
        comment = CommentFactory(user=self.user, is_removed=True)
        self.assertTrue(comment.is_removed)

        url = reverse('wagtail_comments_xtd_publication', kwargs={'comment_pk': comment.id, 'action': 'show'})
        response = self.client.get(url, HTTP_REFERER=XtdCommentAdmin().url_helper.get_action_url('index'))

        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertFalse(comment.is_removed)

    def test_hide_comment(self):
        comment = CommentFactory(user=self.user, is_removed=False)
        self.assertFalse(comment.is_removed)

        url = reverse('wagtail_comments_xtd_publication', kwargs={'comment_pk': comment.id, 'action': 'hide'})
        response = self.client.get(url, HTTP_REFERER=XtdCommentAdmin().url_helper.get_action_url('index'))

        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertTrue(comment.is_removed)

    def test_clear_flags(self):
        comment_flag = CommentFlagFactory(user=self.user)
        comment = comment_flag.comment
        self.assertEqual(comment.flags.count(), 1)

        url = reverse('wagtail_comments_xtd_publication', kwargs={'comment_pk': comment.id, 'action': 'clear_flags'})
        response = self.client.get(url, HTTP_REFERER=XtdCommentAdmin().url_helper.get_action_url('index'))

        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertEqual(comment.flags.count(), 0)
