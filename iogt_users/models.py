import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    first_name = models.CharField('first name', max_length=150, null=True,
                                  blank=True)
    last_name = models.CharField('last name', max_length=150, null=True,
                                 blank=True)
    display_name = models.CharField('display name', max_length=255, null=True, blank=True)
    email = models.EmailField('email address', null=True, blank=True)
    terms_accepted = models.BooleanField(default=False)

    has_filled_registration_survey = models.BooleanField(default=False)
    has_viewed_registration_survey = models.BooleanField(default=False)

    @property
    def is_rapidpro_bot_user(self):
        return self.pk == settings.RAPIDPRO_BOT_USER_ID

    @classmethod
    def get_rapidpro_bot_user(cls):
        return cls.objects.get(pk=settings.RAPIDPRO_BOT_USER_ID)

    @classmethod
    def get_rapidpro_bot_auth_header(cls):
        user = User.objects.get(username=settings.RAPIDPRO_BOT_USER_USERNAME)
        token = RefreshToken.for_user(user)
        return f'Bearer {token.access_token}'


    read_articles = models.ManyToManyField(to='home.Article')

    @classmethod
    def record_article_read(cls, request, article):
        user = request.user
        if user.is_anonymous:
            read_articles = request.session.get('read_articles', [])
            if read_articles:
                if article.pk not in read_articles:
                    # https://code.djangoproject.com/wiki/NewbieMistakes#Appendingtoalistinsessiondoesntwork
                    read_articles = request.session['read_articles']
                    read_articles.append(article.pk)
                    request.session['read_articles'] = read_articles
            else:
                request.session['read_articles'] = [article.pk]
        else:
            if article.id and not user.read_articles.filter(id=article.id).exists():
                user.read_articles.add(article)

    def get_display_name(self):
        return self.display_name or self.username

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
