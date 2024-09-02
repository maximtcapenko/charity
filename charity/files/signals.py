from django.db.models import signals
from django.dispatch import receiver

from .models import Attachment


@receiver(signals.post_delete, sender=Attachment)
def delete_attached_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
