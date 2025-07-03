from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel
from django.utils.timezone import now
from wagtail.fields import RichTextField

class Notification(models.Model):
    head = models.CharField(max_length=255)
    body = models.TextField()
    url = models.URLField(null=True, blank=True)

    groups = models.ManyToManyField(to='auth.Group', related_name='notifications')

    def __str__(self):
        return self.head

@register_snippet
class SignupNotificationTemplate(models.Model):
    title = models.CharField(max_length=255)
    message = RichTextField(features=["bold", "italic", "link", "ul", "ol"])
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(default=now)

    panels = [
        FieldPanel('title'),
        FieldPanel('message'),
        FieldPanel('active'),
    ]

    def __str__(self):
        return f"{self.title} ({'active' if self.active else 'inactive'})"

    class Meta:
        verbose_name = "Signup Notification Template"
        verbose_name_plural = "Signup Notification Templates"

