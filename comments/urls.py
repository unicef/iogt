from __future__ import absolute_import, unicode_literals
from django.conf.urls import url
from django.urls import path

from comments import views
from comments.views import ProcessCannedResponseView, CommentsCommunityModerationView

urlpatterns = [
    url(r'^comment/(?P<comment_pk>\d+)/update/(?P<action>publish|unpublish|hide|show|clear_flags|manual_validated)/$',
        views.update, name='wagtail_comments_xtd_publication'),
    path('comment/<int:comment_pk>/reply',
        views.CommentReplyView.as_view(), name='comment_reply_view'),
    path('comment/new',
            views.post_admin_comment, name='comment_post_admin_comment'),
    path('comment/process-canned-response', ProcessCannedResponseView.as_view(), name='process_canned_response'),
    path('community-moderation/', CommentsCommunityModerationView.as_view(), name='comments_community_moderation'),
]
