from django.contrib.auth.models import User
from django.db import models

from commons.models import Base


class Comment(Base):
    notes = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='comments')
    reply = models.ForeignKey(
        'self', null=True, on_delete=models.SET_NULL, related_name='replies')
    '''use @user_name in comment notes in order to tag user'''
    tagged_interlocutors = models.ManyToManyField(
        User, related_name='tags')

    class Meta:
        ordering = ['date_created']
