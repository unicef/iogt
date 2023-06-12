from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_comments_xtd.models import XtdComment
from factory.django import DjangoModelFactory
import factory

from home.factories import ArticleFactory
from iogt_users.factories import UserFactory


class XtdCommentFactory(DjangoModelFactory):
    comment = "Test comment"
    user = factory.SubFactory(UserFactory)
    content_object = ArticleFactory()

    class Meta:
        model = XtdComment

    @factory.lazy_attribute
    def site_id(self):
        return Site.objects.get_current().id


class CommunityCommentModeratorFactory(UserFactory):
    @factory.post_generation
    def assign_permissions(self, create, extracted, **kwargs):
        if create:
            permission = Permission.objects.get(codename='can_community_moderate')
            self.user_permissions.add(permission)


class AdminCommentModeratorFactory(UserFactory):
    @factory.post_generation
    def assign_permissions(self, create, extracted, **kwargs):
        if create:
            content_type = ContentType.objects.get_for_model(XtdComment)
            permission, created = Permission.objects.get_or_create(
                codename='can_moderate_on_admin_panel',
                content_type=content_type,
            )
            self.user_permissions.add(permission)
