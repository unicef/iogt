from django.db import models


class CommentModerationState(models.TextChoices):
    UNMODERATED = "UNMODERATED", "Unmoderated"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    UNSURE = "UNSURE", "Unsure"


def comment_moderation_choices():
    return [
        ('ALL', 'All'),
        (CommentModerationState.UNMODERATED, CommentModerationState.UNMODERATED.label),
        (CommentModerationState.APPROVED, CommentModerationState.APPROVED.label),
        (CommentModerationState.REJECTED, CommentModerationState.REJECTED.label),
        (CommentModerationState.UNSURE, CommentModerationState.UNSURE.label),
    ]
