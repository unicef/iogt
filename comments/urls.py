from __future__ import absolute_import, unicode_literals
from django.conf.urls import url

from comments import views

urlpatterns = [
    url(r'^comment/(?P<comment_pk>\d+)/update/(?P<action>publish|unpublish|hide|show|clear_flags)/$',
        views.update, name='wagtail_comments_xtd_publication'),
]
