from __future__ import absolute_import, unicode_literals
from django.urls import path

from comments import views


urlpatterns = [
    path('comment/<int:comment_pk>/reply',
        views.CommentReplyView.as_view(), name='comment_reply_view'),
    path('comment/new',
            views.post_admin_comment, name='comment_post_admin_comment'),
    path('comment/process-canned-response', views.ProcessCannedResponseView.as_view(), name='process_canned_response'),
    path('community-moderation/', views.CommentsCommunityModerationView.as_view(), name='comments_community_moderation'),
    path('comment/<int:comment_pk>/approve', views.ApproveCommentView.as_view(), name='approve_comment'),
    path('comment/<int:comment_pk>/reject', views.RejectCommentView.as_view(), name='reject_comment'),
    path('comment/<int:comment_pk>/unsure', views.UnSureCommentView.as_view(), name='unsure_comment'),
    path('comment/<int:comment_pk>/hide', views.HideCommentView.as_view(), name='hide_comment'),
    path('comment/<int:comment_pk>/publish', views.PublishCommentView.as_view(), name='publish_comment'),
    path('comment/<int:comment_pk>/unpublish', views.UnPublishCommentView.as_view(), name='unpublish_comment'),
    path('comment/<int:comment_pk>/clear-flags', views.ClearFlagsCommentView.as_view(), name='clear_flags'),
]
