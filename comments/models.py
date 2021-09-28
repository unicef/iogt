from django.db import models
from django_comments_xtd.models import XtdComment
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page


class CommentableMixin(models.Model):
    """
    Add this mixin to any Model which wants to allow/disallow comments.
    Make sure you update get_absolute_url if this it hasn't already been
    included.

    Use comments_panels to modify allow_comments from the admin.
    """
    allow_comments = models.BooleanField(default=False)

    comments_panels = [
        FieldPanel('allow_comments', heading='Enable?')
    ]

    def get_absolute_url(self):
        if isinstance(self, Page):
            return self.get_url()
        raise NotImplementedError('Implement get_absolute_url for your Model')

    class Meta:
        abstract = True


class CannedResponse(models.Model):
    header = models.TextField(null=True)
    text = models.TextField(null=True)

    def __str__(self):
        return self.text
