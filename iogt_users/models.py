from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    first_name = None
    last_name = None
    display_name = models.CharField(max_length=150, blank=True, null=True)
    has_accepted_terms_and_conditions = models.BooleanField(default=False)

    has_filled_registration_survey = models.BooleanField(default=False)

    class Meta:
        ordering = ('id',)


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}\'s profile'


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
