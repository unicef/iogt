from django.db import models

class AdminNotification(models.Model):
    head = models.CharField(max_length=255)
    body = models.TextField()
    url = models.URLField(null=True, blank=True)

    groups = models.ManyToManyField(to='auth.Group', related_name='admin_notifications')

    def __str__(self):
        return self.head

