import uuid
from django.db import models
from django.contrib.auth.models import User


class Base(models.Model):
    class Meta:
        abstract = True
        ordering = ['-date_created']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    date_created = models.DateTimeField(auto_now_add=True, null=False)


class Notification(Base):
    receiver = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='notifications')
    title = models.CharField(max_length=50)
    url = models.URLField()
    short = models.CharField(max_length=100, blank=False)
    message = models.TextField()
    is_viewed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} ({self.message})'


def get_not_viewed_notifications(self):
    return self.notifications.filter(is_viewed=False)


User.add_to_class('not_viewed_notifications', property(
    fget=get_not_viewed_notifications
))


class Comment(Base):
    notes = models.TextField(blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='comments')
    reply = models.ForeignKey(
        'self', null=True, on_delete=models.SET_NULL, related_name='replies')
    '''use @user_name in comment notes in order to tag user'''
    tagged_interlocutors = models.ManyToManyField(
        User, related_name='tags')
