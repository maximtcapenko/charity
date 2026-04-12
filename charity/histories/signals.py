from django.db.models import signals
from django.dispatch import receiver

from .models import History


audit_event_created = signals.Signal()

@receiver(audit_event_created)
def add_history_record(sender, instance, author, url, name, details, **kwargs):
    History.objects.create(author=author, name=name, url=url, details=details, target=instance)
    