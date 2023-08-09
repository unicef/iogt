from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_comments_xtd.models import XtdComment
from django_comments.models import CommentFlag
from factory.django import DjangoModelFactory
import factory

from home.factories import ArticleFactory
from iogt_users.factories import UserFactory


class CommentFactory(DjangoModelFactory):
    comment = "Test comment"
    user = factory.SubFactory(UserFactory)
    content_object = factory.SubFactory(ArticleFactory)

    class Meta:
        model = XtdComment

    @factory.lazy_attribute
    def site_id(self):
        return Site.objects.get_current().id


class FlagFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    comment = factory.SubFactory(CommentFactory)
    flag = CommentFlag.SUGGEST_REMOVAL

    class Meta:
        model = CommentFlag


class CommunityModeratorFactory(UserFactory):
    first_name = "Community"
    last_name = "Moderator"

    @factory.post_generation
    def assign_permissions(self, create, extracted, **kwargs):
        if create:
            permission = Permission.objects.get(codename='can_community_moderate')
            self.user_permissions.add(permission)


class AdminModeratorFactory(UserFactory):
    first_name = "Admin"
    last_name = "Moderator"

    @factory.post_generation
    def assign_permissions(self, create, extracted, **kwargs):
        if create:
            permission = Permission.objects.get(
                codename='can_moderate',
                content_type=ContentType.objects.get_for_model(XtdComment),
            )
            self.user_permissions.add(permission)
