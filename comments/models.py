from django.db import models
from django.utils import timezone
from django_comments_xtd.models import XtdComment
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page


class CommentStatus:
    OPEN = 'open'
    CLOSED = 'closed'
    DISABLED = 'disabled'
    TIMESTAMPED = 'timestamped'
    INHERITED = 'inherited'

    Choices = (
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (DISABLED, 'Disabled'),
        (TIMESTAMPED, 'Timestamped'),
        (INHERITED, 'Inherited'),
    )


class CommentableMixin(models.Model):
    """
    Add this mixin to any Model which wants to allow/disallow comments.
    Make sure you update get_absolute_url if this it hasn't already been
    included.

    Use comments_panels to modify commenting_status from the admin.
    """
    commenting_status = models.CharField(max_length=15, choices=CommentStatus.Choices, default=CommentStatus.INHERITED)
    commenting_starts_at = models.DateTimeField(null=True, blank=True)
    commenting_ends_at = models.DateTimeField(null=True, blank=True)

    comments_panels = [
        FieldPanel('commenting_status', heading='Status'),
        FieldPanel('commenting_starts_at', heading='Commenting Opens At'),
        FieldPanel('commenting_ends_at', heading='Commenting Ends At')

    ]

    def should_show_comments_list(self):
        return self.commenting_status in [
            CommentStatus.OPEN, CommentStatus.CLOSED, CommentStatus.TIMESTAMPED, CommentStatus.INHERITED
        ]

    def should_show_new_comment_box(self):
        from home.models import Section

        commenting_still_valid = True
        commenting_status = self.commenting_status
        commenting_starts_at = self.commenting_starts_at
        commenting_ends_at = self.commenting_ends_at

        if commenting_status == CommentStatus.INHERITED:
            ancestors = self.get_ancestors().type(Section).specific().order_by('-path')
            for ancestor in ancestors:
                if ancestor.commenting_status in [
                    CommentStatus.OPEN, CommentStatus.CLOSED, CommentStatus.DISABLED, CommentStatus.TIMESTAMPED]:
                    commenting_status = ancestor.commenting_status
                    commenting_starts_at = ancestor.commenting_starts_at
                    commenting_ends_at = ancestor.commenting_ends_at
                    break

        if commenting_starts_at:
            commenting_still_valid = commenting_starts_at < timezone.now()
        if commenting_ends_at:
            commenting_still_valid = commenting_still_valid and commenting_ends_at > timezone.now()

        return commenting_status == CommentStatus.OPEN or \
               (commenting_status == CommentStatus.TIMESTAMPED and commenting_still_valid)

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
