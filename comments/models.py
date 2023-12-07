from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_comments.signals import comment_was_flagged
from django_comments_xtd.models import XtdComment
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page

from comments import get_comments_moderation_class

User = get_user_model()
Moderator = get_comments_moderation_class()


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


class CommentModerationState(models.TextChoices):
    UNMODERATED = "UNMODERATED", "Unmoderated"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    UNSURE = "UNSURE", "Unsure"


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

    def _get_valid_ancestor_for_commenting(self):
        from home.models import Section

        ancestors = self.get_ancestors().type(Section).specific().order_by('-path')
        for ancestor in ancestors:
            if ancestor.commenting_status in [
                CommentStatus.OPEN, CommentStatus.CLOSED, CommentStatus.DISABLED, CommentStatus.TIMESTAMPED]:
                return ancestor

    def should_show_comments_list(self):
        commenting_status = self.commenting_status
        if commenting_status == CommentStatus.INHERITED:
            ancestor = self._get_valid_ancestor_for_commenting()
            commenting_status = ancestor.commenting_status if ancestor else CommentStatus.DISABLED

        return commenting_status in [CommentStatus.OPEN, CommentStatus.CLOSED, CommentStatus.TIMESTAMPED]

    def should_show_new_comment_box(self):
        commenting_still_valid = True
        commenting_status = self.commenting_status
        commenting_starts_at = self.commenting_starts_at
        commenting_ends_at = self.commenting_ends_at

        if commenting_status == CommentStatus.INHERITED:
            ancestor = self._get_valid_ancestor_for_commenting()
            if ancestor:
                commenting_status = ancestor.commenting_status
                commenting_starts_at = ancestor.commenting_starts_at
                commenting_ends_at = ancestor.commenting_ends_at
            else:
                commenting_status = CommentStatus.DISABLED
                commenting_starts_at = None
                commenting_ends_at = None

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


class CommunityCommentModeration(models.Model):
    state = models.CharField(
        choices=CommentModerationState.choices,
        default=CommentModerationState.UNMODERATED,
        max_length=255,
    )
    comment = models.OneToOneField(
        to='django_comments_xtd.XtdComment',
        related_name='comment_moderation',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.comment.id} | {self.state}'

    class Meta:
        permissions = (
            ("can_community_moderate", "Can moderate comments on public site"),
        )


@receiver(post_save, sender=XtdComment)
def comment_moderation_handler(sender, instance, created, **kwargs):
    if created:
        moderator = Moderator()
        instance.is_public = moderator.moderate(instance)
        instance.save(update_fields=['is_public'])
        CommunityCommentModeration.objects.create(comment_id=instance.id)


@receiver(comment_was_flagged, sender=XtdComment)
def comment_flagged(sender, comment, **kwargs):
    if hasattr(comment, 'comment_moderation'):
        comment_moderation = comment.comment_moderation
        comment_moderation.state = CommentModerationState.UNMODERATED
        comment_moderation.save(update_fields=['state'])
