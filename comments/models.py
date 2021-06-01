from django.db import models
from django_comments_xtd.models import XtdComment


class AllowCommentsModelMixin(models.Model):
    """
    Add this mixin to any Model which wants to allow/disallow comments
    """
    allow_comments = models.BooleanField(default=True)

    class Meta:
        abstract = True
