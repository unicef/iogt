import factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_comments.models import CommentFlag
from django_comments_xtd.models import XtdComment
from factory.django import DjangoModelFactory

from home.models import Article
from iogt_users.factories import UserFactory


class CommentFactory(DjangoModelFactory):
    content_type = factory.LazyAttribute(lambda o: ContentType.objects.get_for_model(Article))
    site = factory.LazyAttribute(lambda o: Site.objects.get_current())
    comment = factory.Sequence(lambda n: 'Comment{0}'.format(n))
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = XtdComment


class CommentFlagFactory(DjangoModelFactory):
    comment = factory.SubFactory(CommentFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = CommentFlag
