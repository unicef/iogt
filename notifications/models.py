from django.db import models


class Notification(models.Model):
    head = models.CharField(max_length=255)
    body = models.TextField()
    url = models.URLField(null=True, blank=True)

    groups = models.ManyToManyField(to='auth.Group', related_name='notifications')

    def __str__(self):
        return self.head
