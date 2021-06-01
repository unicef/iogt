from __future__ import absolute_import, unicode_literals
from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^$', pages, name='wagtail_comments_xtd_pages'),
    url(r'^(?P<pk>\d+)/$', comments, name='wagtail_comments_xtd_comments'),
    url(r'^(?P<page_pk>\d+)/comment/(?P<comment_pk>\d+)/thread/$',
        comment_thread, name='wagtail_comments_xtd_comment_thread'),
    url(r'^(?P<page_pk>\d+)/comment/(?P<comment_pk>\d+)/update/(?P<action>publish|unpublish|hide|show)/$',
        update, name='wagtail_comments_xtd_publication'),
]
