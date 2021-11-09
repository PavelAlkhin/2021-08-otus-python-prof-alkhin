from tkinter import Image

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import Textarea
from PIL import Image


def user_directory_path(user, filename):
    """file will be uploaded to MEDIA_ROOT / user_<id>/<filename>"""
    return 'db_app/static/db_app/img/user_{0}/{1}'.format(user.id, filename)


class Tag(models.Model):
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    tag = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.tag}'


class UserProfile(models.Model):
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profilies'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(max_length=50)
    avatar = models.FileField(upload_to=user_directory_path)
    register_date = models.DateField()
    email = models.EmailField()

    def save(self, *args, **kwargs):
        super().save()
        if self.avatar:
            fn = user_directory_path(self.user, self.avatar)
            img = Image.open(fn)  # Open image using self

            if img.height > 16 or img.width > 16:
                new_img = (64, 64)
                img.thumbnail(new_img)
                img.save(fn)  # saving image at the same path

    def __str__(self):
        return f'{self.user} {self.nick_name}'


class Question(models.Model):
    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    title = models.CharField(max_length=150)
    description = models.TextField(max_length=550)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return f'{self.title} {self.author} {self.date}'


class Answer(models.Model):
    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    description = models.TextField(max_length=550)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    is_right = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.author} {self.date} {self.is_right}'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
