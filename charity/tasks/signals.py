from django.db.models import signals
from django.dispatch import receiver

from .models import Task


@receiver(signals.post_save, sender=Task)
def add_default_subscribers_wheb_task_added(sender, instance, created, **kwargs):
    if created:
        """When task has been created we add to default subscribers next users
        - task author
        - task assignee
        - project leader
        - task reviewer
        """
        project = instance.project
        subscribers = list(instance.subscribers.all())

        if not project.leader in subscribers:
            instance.subscribers.add(project.leader)
        if instance.assignee not in subscribers:
            instance.subscribers.add(instance.assignee)
        if not instance.author in subscribers:
            instance.subscribers.add(instance.author)
        if instance.reviewer_id and not instance.reviewer in subscribers:
            instance.subscribers.add(instance.reviewer)
