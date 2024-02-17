import os

from django.db.models import signals
from django.dispatch import receiver

from .models import Attachment


@receiver(signals.post_delete, sender=Attachment)
def delete_attached_file(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
